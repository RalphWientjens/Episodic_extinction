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
from psychopy import core, visual, event, logging
import random
# from psychopy.core import getMouse
import os
import sys
import yaml
import serial
from pathlib import Path
import hedfpy

PHASES = {
    "CS":               ("CS", 3.0),
    "CS_distress":      ("CS_distress", 4.0),
    "US":               ("US", 4.0),
    "EXT":              ("fixcross", 4.0),
    "coherence":        ("coherence", 4.0),
    "reinforced_EXT":   ("fixcross", 4.0),  # duration defined per phase
    "fixcross":         ("fixcross", (4,8)),
    "fixcross_long":    ("fixcross", (8, 12)),
}

SESSION_CONFIG = {
    1: dict(
        base=["CS", "CS_distress", "US"],
        coherence_last_block=True,
    ),

    2: dict(
        CC=["CS", "CS_distress", "US"],
        EXT=["CS", "CS_distress", "EXT"],
        coherence_last_block=True,
    ),

    3: dict(
        reinforced=["CS", "CS_distress", "US"],
        EXT=["CS", "CS_distress", "EXT"],
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
        # uneven (1 of 5) → CC, even (2 of 4) → EXT
        return "CC" if condition % 2 == 1 else "EXT"

    if sess == 3:
        # reinforced if condition == 6 OR uneven
        if condition == 6 or condition % 2 == 1:
            return "reinforced"
        else:
            return "EXT"

    raise ValueError(f"Unknown session: {sess}")

# functions for randomisation of trials
# checking function for two conditions and three valence
def is_valid_sequence(pool_df):
    """Check if a trial pool has no more than 2 consecutive episodes of the same valence."""
    for i in range(len(pool_df) - 2):
        if (
            pool_df["valence"].iloc[i]
            == pool_df["valence"].iloc[i + 1]
            == pool_df["valence"].iloc[i + 2]
        ):
            return False
    return True


def pseudorandomize_stimset(stimset, max_attempts=10000, seed=None):
    """
    Randomize stimset grouped by trial pools (1-6).
    Within each block:
    - Trial pool 1 comes first, then 2, then 3, etc.
    - Within each trial pool, episodes are randomized
    - Constraint: no more than 2 consecutive episodes of the same valence
    """
    if seed is not None:
        random.seed(seed)

    # Group by trial pool
    trial_pools = {trial_num: group.reset_index(drop=True) 
                   for trial_num, group in stimset.groupby('trial', sort=True)}
    
    result_rows = []
    
    # Process each trial pool in order (1, 2, 3, 4, 5, 6)
    for trial_num in sorted(trial_pools.keys()):
        pool_df = trial_pools[trial_num].copy()
        
        # Randomize within the pool until valid
        for attempt in range(max_attempts):
            shuffled_pool = pool_df.sample(frac=1).reset_index(drop=True)
            
            if is_valid_sequence(shuffled_pool):
                result_rows.append(shuffled_pool)
                break
        else:
            raise RuntimeError(f"Could not generate valid sequence for trial pool {trial_num} after {max_attempts} attempts")
    
    # Concatenate all pools in order
    final_df = pd.concat(result_rows, ignore_index=True)
    final_df = final_df.copy()
    final_df["presentation_order"] = range(1, len(final_df) + 1)
    
    return final_df


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
                 test_mode=False,
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

        # Hide mouse cursor based on settings
        self.win.mouseVisible = self.settings["mouse"]["visible"]

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

        self.break_duration = 75  # default break duration in seconds, can be overridden by instructions
        self.get_ready_duration = 5  # default get ready duration in seconds, can be overridden by instructions
        
        if self.test_mode:
            self.break_duration = 10  # shorter break duration in test mode
            self.get_ready_duration = 5  # shorter get ready duration in test mode

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
        practice_phase_names = ["CS", "CS_distress", "US", "coherence", "fixcross"]

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
            core.wait(duration)  # convert to minutes
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
                duration *= 0.05  # speed up for testing

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

    def create_us_trials(self):
        """Create a block of US trials, prior to session 1 only.
        
        Presents each unique US stimulus followed by a fixation cross.
        """
        us_trials = []
        
        # Randomize order uniquely per block
        randomized_stims = pseudorandomize_stimset(
            self.stimset,
            seed=None
        )

        # Get unique US stimuli from the stimset
        unique_us = randomized_stims['US'].unique()
        us_sounds = randomized_stims.groupby('US')['US_sound'].first()
        
        phase_names = ['US', 'fixcross']
        
        for trial_nr, us_stim in enumerate(unique_us):
            us_sound = us_sounds[us_stim]
            
            # Set durations for habituation block
            phase_durations = [4, random.randint(5,7)]  # US: 4s, fixcross: 5-7s
            
            if self.test_mode:
                phase_durations = [d * 0.01 for d in phase_durations]
            
            # Create parameters dict
            params = {
                'US': us_stim,
                'US_sound': us_sound,
                'CS': '',  # Not used in habituation
                'block': 0,  # habituation block
                'episode_nr': trial_nr + 1,
                'condition': 0,
                'valence': 0,
            }
            
            trial = ExtinctionTrial(
                session=self,
                phase_names=phase_names,
                phase_durations=phase_durations,
                trial_nr=trial_nr,
                parameters=params,
            )
            
            us_trials.append(trial)
        
        return us_trials

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

        # US habituation block for session 1 only (BEFORE practice)
        if self.sess == 1:
            self.show_text_screen(
                self.instructions["session_1"]["US_block"][0]
            )

            self.show_text_screen(
                text = self.instructions["session_1"]["US_prepare"][0],
                duration = 3  # 5 seconds
            )
            
            self.start_experiment()
            
            us_trials = self.create_us_trials()
            for trial in us_trials:
                trial.run()

        # practice trials for session 1 only
        if self.sess == 1:
            self.show_text_screen(
                self.instructions["session_1"]["practice_start"][0]
            )

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

            self.show_text_screen(
                text = self.instructions["before_start"],
                duration = 5  # 5 seconds
            )
            
            #start experiment timing for sessions 2 and 3
            self.start_experiment()

        for block_idx, block_trials in enumerate(self.trials_by_block):

            # Between-block instructions (not before block 1)
            if block_idx > 0:
                block_text = self.instructions[f"session_{self.sess}"]["between_blocks"][0].format(block=block_idx)
                self.show_text_screen(
                    text=block_text, 
                    duration = self.break_duration  # break duration in seconds
                )
                # calibrate tracker again after break, if applicable
                # if self.eyetracker_on:
                #     self.calibrate_eyetracker()

                # other approach: stop and start the eyetracker, during calibration. Still to test!
                if self.eyetracker_on:
                    self.stop_recording_eyetracker()
                    self.calibrate_eyetracker()
                    self.start_recording_eyetracker()
                
                block_text = self.instructions[f"session_{self.sess}"]["end of break"][0].format(block=block_idx)
                self.show_text_screen(
                    text=block_text,
                    duration = self.get_ready_duration  # get ready duration in seconds
                )


            for trial in block_trials:
                trial.run()

        # End experiment (also stops eyetracking recording)
        self.close()

    def close(self):
        # Close base - PylinkEyeTrackerSession will download the EDF file from the EyeLink Host PC and save it in the session output directory.
        super().close()

        # Check for EDF file
        if isinstance(self, PylinkEyetrackerSession) and self.eyetracker_on:
            # Note that following filename is taken from PylinkEyetrackerSession::close() and will thus break if dependency is changed.
            edfFile = Path(self.output_dir).joinpath(self.output_str + '.edf')
            if not edfFile.exists() or not edfFile.is_file():
                logging.warning(f"Expected EyeLink EDF file {edfFile} does not exist")
                return

            hdf5Filename = edfFile.with_suffix(".hdf5")
            # Convert to HDF5
            eyeOperator = hedfpy.HDFEyeOperator(str(hdf5Filename))
            eyeOperator.add_edf_file(str(edfFile))
            eyeOperator.edf_message_data_to_hdf()
            eyeOperator.edf_gaze_data_to_hdf()
