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
# from psychopy.core import getMouse
import os
import sys


class ExtinctionSession(Session):
    """
    Session class for the Episodic Extinction experiment.
    
    Manages the experimental session including trial sequence,
    instructions, and data collection.
    """
    
    def __init__(self, output_str, output_dir=None, settings_file="expsettings.yml", sess=1):
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
        super().__init__(output_str, output_dir=output_dir, 
                        settings_file=settings_file)

        self.sess = sess  # Store session number

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


        stimset_path = os.path.join(
            os.path.dirname(__file__),
            "stimuli_files",
            "stimuli_list_test.tsv"
        )

        self.stimset = pd.read_csv(stimset_path, sep="\t")

        self.n_trials = len(self.stimset)
        
        # Experiment-specific parameters
        # Can be overridden by settings file
        if hasattr(self, 'settings') and 'experiment' in self.settings:
            self.n_trials = self.settings['experiment'].get('n_trials', 2)
            self.trial_duration = self.settings['experiment'].get('trial_duration', 17.0)
        else:
            self.n_trials = 2  # Default number of trials
        
    def create_trials(self, blocks=3):
        """Create trial list for the session."""
        self.trials = []

        self.blocks = blocks
        trial_counter = 0
        
        #Now loop over blocks, for fMRI make unique blocks per run (so no loop needed, just import run number from main)
        for block in range(self.blocks):

            for trial_nr, stim_row in self.stimset.iterrows():
                
                # Define phases for each trial
                # Using instance variables for flexibility
                phase_durations = [1.0, 3.0, 1.0, 3.0, 4.0, 4.0, 1.0, 4.0, 1.0]
                phase_names = ["context", "NS", "context", "CS", "CS_distress", "US", "context", "coherence", "fixcross"]

                # declare parameters
                params = stim_row.to_dict()
                params['block'] = block + 1

                # Create trial
                trial = ExtinctionTrial(
                    session=self,
                    trial_nr=trial_nr,
                    phase_durations=phase_durations,
                    phase_names=phase_names,
                    parameters = params
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
        
        # Run all trials
        for trial in self.trials:
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
