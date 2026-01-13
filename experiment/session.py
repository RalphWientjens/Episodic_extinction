"""
Created on Sun Jan 4th 12:00:00 2026

@author: Ralph Wientjens

Session class for Episodic Extinction experiment.
"""

from exptools2.core import PylinkEyetrackerSession
from exptools2.core import Session
from trial import ExtinctionTrial
import numpy as np
import pandas as pd
from psychopy import visual
import random
# from psychopy.core import getMouse
import os
import sys

PHASES = {
    "context":          ("context", 1.0),
    "NS":               ("NS", 3.0),
    "CS":               ("CS", 3.0),
    "CS_only":          ("CS_only", 3.0),
    "CS_distress":      ("CS_distress", 4.0),
    "CS_distress_only": ("CS_distress_only", 4.0),
    "US":               ("US", 4.0),
    "US_only":          ("US_only", 4.0),
    "EXT":              ("context", 4.0),
    "coherence":        ("coherence", 4.0),
    "reinforced_EXT":   ("fixcross", 4.0),  # duration defined per phase
    "fixcross":         ("fixcross", (1,3)),
    "fixcross_long":    ("fixcross", (5, 7)),
}

SESSION_CONFIG = {
    1: dict(
        base=["context", "NS", "context", "CS", "CS_distress", "US", "context"],
        coherence_last_block=True,
    ),

    2: dict(
        CC=["context", "CS", "CS_distress", "US", "context"],
        EXT=["context", "CS", "CS_distress", "EXT", "context"],
        coherence_last_block=True,
    ),

    3: dict(
        reinforced=["CS_only", "CS_distress_only", "US_only"],
        EXT=["CS_only", "CS_distress_only", "reinforced_EXT"],
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
        if condition == 10 or condition % 2 == 1:
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


class ExtinctionSession(Session):
    """
    Session class for the Episodic Extinction experiment.
    
    Manages the experimental session including trial sequence,
    instructions, and data collection.
    """
    
    def __init__(self, output_str, output_dir=None, settings_file="expsettings.yml", sess=None, version=None, test_mode=True, blocks=3):
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
        super().__init__(
            output_str, 
            output_dir=output_dir, 
            settings_file=settings_file)

        self.sess = sess  # Store session number
        self.version = version  # Store version number
        self.test_mode = test_mode

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

        #load stimulus set based on version and session
        #load day 1 practice stimset, to be done prior to start of session 1
        practice_stimset_path = os.path.join(
            os.path.dirname(__file__),
            "Practice_stimsets",
            f"day1_practice_stimset.tsv"
        )
        self.practice_stimset = pd.read_csv(practice_stimset_path, sep="\t")
        practice_phase_names = ["context", "NS", "context", "CS", "CS_distress", "US", "context", "coherence", "fixcross"]

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

            phase_names.append(phase_key)
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
                is_last_block=True,   # ← KEY LINE
            )

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
        """Create trial list for the session."""
        self.trials = []
        trial_counter = 0
        
        #Add practice trials for session 1
        if self.sess == 1:
            practice_trials = self.create_practice_trials()
            self.trials.extend(practice_trials)

        #Now loop over blocks, for fMRI make unique blocks per run (so no loop needed, just import run number from main for each block)
        for block in range(self.blocks):

            is_last_block = (block == self.blocks - 1)

            # Randomize order uniquely per block
            randomized_stimset = pseudorandomize_stimset(
                self.stimset,
                seed=None  # or use subject/block-based seed
            )

            for trial_nr, stim_row in randomized_stimset.iterrows():

                # declare parameters
                params = stim_row.to_dict()
                params['block'] = block + 1

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

                self.trials.append(trial)
                trial_counter += 1
    


    def run(self):
        """Run the experimental session."""
        # Display instructions
        # self.display_instructions()
        
        # Create trials
        self.create_trials()
        
        # Start experiment
        self.start_experiment()
        
        # --- Run practice trials first (session 1 only) ---
        if self.sess == 1:
            for trial in self.trials:
                if trial.parameters.get("practice", False):
                    trial.run()

            # ⏸ PAUSE AFTER PRACTICE
            self.visual.show_text(
                "End of practice.\n\n"
                "If you have any questions, ask the experimenter now.\n\n"
                "Press SPACE to continue."
            )
            self.wait_for_keypress("space")

        # --- Run main trials ---
        for trial in self.trials:
            if not trial.parameters.get("practice", False):
                trial.run()

        # End experiment
        self.close()

    # def display_instructions(self):
    #     """Display instruction screen."""
    #     instruction_text = """
    #     Welcome to the Episodic Extinction Experiment
        
    #     You will see a series of stimuli on the screen.
    #     Please respond as instructed.
        
    #     Press any key to continue...
    #     """
        
    #     instruction_stim = visual.TextStim(
    #         self.win,
    #         text=instruction_text,
    #         height=0.1,
    #         wrapWidth=1.5,
    #         color='white'
    #     )
        
    #     instruction_stim.draw()
    #     self.win.flip()
        
    #     # Wait for key press
    #     self.win.waitKeys()
