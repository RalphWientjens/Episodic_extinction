"""
Created on Sun Jan 4th 12:00:00 2026

@author: Ralph Wientjens

Session class for Episodic Extinction experiment.
"""

from exptools2.core import PylinkEyetrackerSession #Set on if eyetracker is used, otherwise use Session
from exptools2.core import Session
from trial import ExtinctionTrial
import numpy as np
import pandas as pd
from psychopy import core, visual, event
import random
# from psychopy.core import getMouse
import os
import sys
import yaml
import serial

PHASES = {
    "context":          ("context", 1.0),
    "NS":               ("NS", 3.0),
    "CS":               ("CS", 4.0),
    "CS_only":          ("CS_only", 3.0),
    "CS_distress":      ("CS_distress", 4.0),
    "CS_distress_only": ("CS_distress_only", 4.0),
    "US":               ("US", 4.0),
    "US_only":          ("US_only", 4.0),
    "EXT":              ("fixcross", 4.0),
    "coherence":        ("coherence", 4.0),
    "reinforced_EXT":   ("fixcross", 4.0),  # duration defined per phase
    "fixcross":         ("fixcross", (1,3)),
    "fixcross_long":    ("fixcross", (8, 12)),
}

SESSION_CONFIG = {
    1: dict(
        base=["CS", "US"],
        coherence_last_block=True,
    ),

    2: dict(
        CC=["CS", "US"],
        EXT=["CS", "EXT"],
        coherence_last_block=True,
    ),

    3: dict(
        reinforced=["CS","US"],
        EXT=["CS", "EXT"],
        coherence_last_block=False,
    ),
}

def resolve_condition_label(sess: int, condition: int) -> str:
    """
    Maps (session, condition integer) to a condition label
    used in SESSION_CONFIG.
    """

    if sess == 1:
        return "base"

    if sess == 2:
        # uneven → CC, even → EXT
        return "CC" if condition % 2 == 1 else "EXT"

    if sess == 3:
        # reinforced if condition == 10 OR uneven
        if condition == 6 or condition % 2 == 1:
            return "reinforced"
        else:
            return "EXT"

    raise ValueError(f"Unknown session: {sess}")

# functions for randomisation of trials
# checking function for two conditions and three valence
def is_valid_sequence(df):
    # No more than 2 identical conditions in a row
    for i in range(len(df) - 2):
        if (
            df["condition"].iloc[i]
            == df["condition"].iloc[i + 1]
            == df["condition"].iloc[i + 2]
        ):
            return False

    # No more than 3 identical valences in a row
    for i in range(len(df) - 3):
        if (
            df["valence"].iloc[i]
            == df["valence"].iloc[i + 1]
            == df["valence"].iloc[i + 2]
            == df["valence"].iloc[i + 3]
        ):
            return False

    return True

# in case we want reproducible seeds per subject/session
# seed = hash(f"{self.output_str}_block{block}") % (2**32)

#Create psuedorandom stimset order
def pseudorandomize_stimset(stimset, max_attempts=10000, seed=None):

    if seed is not None:
        random.seed(seed)

    for _ in range(max_attempts):
        shuffled = stimset.sample(frac=1).reset_index(drop=True)

        if is_valid_sequence(shuffled):
            shuffled = shuffled.copy()
            shuffled["presentation_order"] = range(1, len(shuffled) + 1)
            return shuffled

    raise RuntimeError("Could not generate a valid sequence.")


class ExtinctionSession(PylinkEyetrackerSession):
    """
    Session class for the Episodic Extinction experiment.
    Manages the experimental session including trial sequence,
    instructions, and data collection.
    """

    def __init__(self,
                 output_str,
                 output_dir=None,
                 settings_file="expsettings.yml",
                 sess=None,
                 version=None,
                 OS="windows",
                 test_mode=True,
                 blocks=3,
                 enable_eyetracker=False,
                 enable_serial_markers=False,
                 enable_parallel_markers=False):
        """
        Initialize ExtinctionSession.

        Parameters
        ----------
        output_str : str
            Basename for output files
        output_dir : str, optional
            Directory for output files
        settings_file : str, optional
            Path to settings file
        """
        # Load the settings now, since we need them as a parameter to load ourselves.
        tempSettings = Session(output_str=output_str, output_dir=output_dir, settings_file=settings_file).settings

        super().__init__(
            output_str,
            output_dir=output_dir,
            settings_file=settings_file,
            eyetracker_on = tempSettings["test_settings"]["eyetracker_on"])

        if sys.platform == 'win32':
            from ctypes import windll

        # Open serial port
        self.enable_serial_markers = self.settings["test_settings"]["serial_markers_on"]
        if self.enable_serial_markers:
            self.serialPort = serial.Serial("COM3", baudrate=115200)

        self.enable_parallel_markers = self.settings["test_settings"]["parallel_markers_on"]
        if self.enable_parallel_markers:
            currentDir = os.path.dirname(os.path.realpath(__file__))
            windll.LoadLibrary(currentDir + "/inpoutx64.dll")     # uncomment when running on Windows and using parallel port, make sure to have the inpoutx64.dll in the same directory as this script
            from psychopy import parallel
            self.parallelPort = parallel.ParallelPort(address='0x3FF8')

        self.sess = sess  # Store session number
        self.version = version  # Store version number
        self.test_mode = self.settings["test_settings"]["test_mode_on"]  # Store test mode flag

        # blocks per session
        self.session_to_blocks = {
        1: 3,
        2: 4,
        3: 1,
        }

        try:
            self.blocks = self.session_to_blocks[self.sess]
        except KeyError:
            print(f"Error: Session {self.sess} is not defined. Please provide a valid session number (1, 2, or 3).")
            sys.exit(1)

        instructions_path = os.path.join(
            os.path.dirname(__file__),
            "Instructions.yml",)

        with open(instructions_path, 'r') as file:
            self.instructions = yaml.safe_load(file)

        #load stimulus set based on version and session
        #load day 1 practice stimset, to be done prior to start of session 1
        practice_stimset_path = os.path.join(
            os.path.dirname(__file__),
            "Practice_stimsets",
            "day1_practice_stimset.tsv"
        )
        self.practice_stimset = pd.read_csv(practice_stimset_path, sep="\t")
        practice_phase_names = ["context", "NS", "context", "CS", "CS_distress", "US", "context", "coherence", "fixcross"]

        if self.practice_stimset.empty:
            raise RuntimeError("Practice stimset contains no trials.")

        # stimset_path = os.path.join(
        #     os.path.dirname(__file__),
        #     "stimuli_files",
        #     "stimuli_list_test.tsv"
        # )

        stimset_path = os.path.join(
            os.path.dirname(__file__),
            "Stimsets",
            f"version{self.version}_day{self.sess}.tsv"
        )

        self.stimset = pd.read_csv(stimset_path, sep="\t")
        self.n_trials = len(self.stimset)


    def show_text_screen(self, text, height=28, color="black", wait_keys=None, duration=None):
        """Show a full-screen text and wait for key press."""

        msg = visual.TextStim(
            win=self.win,
            text=text,
            height=height,
            color=color,
            font="Arial",
            wrapWidth=0.9 * self.win.size[0],
        )

        msg.draw()
        self.win.flip()

        # Clear old key presses
        event.clearEvents(eventType="keyboard")

        if duration is not None:
            # Wait for specified duration
            core.wait(duration * 60)  # convert to minutes
        else:
            # Wait for allowed keys
            event.waitKeys(keyList=list(wait_keys or ["space"]))

    # add instruction helper function
    def show_instruction_sequence(self, texts, **format_kwargs):
        for text in texts:
            self.show_text_screen(text.format(**format_kwargs))


    def get_phases_for_trial(self, condition_label: str, is_last_block: bool):
        """Get phase names and durations for a trial, based off the session and condition."""
        cfg = SESSION_CONFIG[self.sess]

        base_phases = cfg[condition_label].copy()

        if is_last_block and cfg.get("coherence_last_block", False):
            base_phases.append("coherence")
            base_phases.append("fixcross")

        else:
            base_phases.append("fixcross_long")

        phase_names = []
        phase_durations = []

        for phase_key in base_phases:
            draw_name, duration = PHASES[phase_key]

            if isinstance(duration, tuple):
                lo, hi = duration
                duration = random.randint(lo,hi)

            if self.test_mode:
                duration *= 0.1  # speed up for testing

            phase_names.append(draw_name)
            phase_durations.append(duration)

        return dict(names=phase_names, durations=phase_durations)

    def create_practice_trials(self):
        """Create practice trials for session 1 only."""
        practice_trials = []

        # practice uses last-block phase structure
        for trial_nr, stim_row in self.practice_stimset.iterrows():

            params = stim_row.to_dict()
            params["block"] = 0
            params["practice"] = True

            condition_value = int(stim_row["condition"])
            condition_label = resolve_condition_label(self.sess, condition_value)

            phases = self.get_phases_for_trial(
                condition_label=condition_label,
                is_last_block=True,
            )

            if trial_nr == 0:
                print("Practice trial phases:", phases["names"])
                print("Practice trial durations:", phases["durations"])
                print(params)

            trial = ExtinctionTrial(
                session=self,
                phase_names=phases["names"],
                phase_durations=phases["durations"],
                trial_nr=trial_nr,
                parameters=params,
            )

            practice_trials.append(trial)

        return practice_trials

    def create_trials(self):
        """Create practice and main trials for the session."""

        # practice trials
        self.practice_trials = []

        if self.sess == 1:
            self.practice_trials = self.create_practice_trials()
            print(f"Created {len(self.practice_trials)} practice trials")


        # main trials, by block
        self.trials_by_block = []

        for block in range(self.blocks):

            is_last_block = (block == self.blocks - 1)

            # Randomize order uniquely per block
            randomized_stimset = pseudorandomize_stimset(
                self.stimset,
                seed=None
            )

            block_trials = []

            for trial_nr, stim_row in randomized_stimset.iterrows():

                params = stim_row.to_dict()
                params["block"] = block + 1

                condition_value = int(stim_row["condition"])
                condition_label = resolve_condition_label(self.sess, condition_value)

                phases = self.get_phases_for_trial(
                    condition_label=condition_label,
                    is_last_block=is_last_block
                )

                trial = ExtinctionTrial(
                    session=self,
                    phase_names=phases["names"],
                    phase_durations=phases["durations"],
                    trial_nr=trial_nr,
                    parameters=params
                )

                block_trials.append(trial)

            self.trials_by_block.append(block_trials)

    def run(self):
        """Run the experimental session."""

        # Create main trials
        self.create_trials()

        # session instructions
        session_key = f"session_{self.sess}"
        self.show_instruction_sequence(
            self.instructions[session_key]["before_session"]
        )

        # Tracker calibration
        if self.eyetracker_on:
            self.calibrate_eyetracker()

            # Start recording
            self.start_recording_eyetracker()

        # practice trials for session 1 only
        if self.sess == 1:
            self.show_text_screen(
                self.instructions["session_1"]["practice_start"][0]
            )

            # start experiment timing for session 1
            self.start_experiment()

            for trial in self.practice_trials:
                trial.run()

            # Pause after practice
            self.show_text_screen(
                self.instructions["session_1"]["practice_end"][0]
            )
            # self.clock.reset()  # reset clock after practice

        else:
            self.show_instruction_sequence(
                self.instructions[session_key]["Start instructions"]
            )
            #start experiment timing for sessions 2 and 3
            self.start_experiment()

        for block_idx, block_trials in enumerate(self.trials_by_block):

            # Between-block instructions (not before block 1)
            if block_idx > 0:
                block_text = self.instructions[f"session_{self.sess}"]["between_blocks"][0].format(block=block_idx)
                self.show_text_screen(
                    text=block_text,
                    duration = 1.25  # 30 seconds
                )
                block_text = self.instructions[f"session_{self.sess}"]["end of break"][0].format(block=block_idx)
                self.show_text_screen(
                    text=block_text,
                    duration = 0.25  # 30 seconds
                )


            for trial in block_trials:
                trial.run()

        # End experiment (also stops eyetracking recording)
        self.close()