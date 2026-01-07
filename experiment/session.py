"""
Created on Sun Jan 4th 12:00:00 2026

@author: Ralph Wientjens

Session class for Episodic Extinction experiment.
"""

from exptools2.core import PylinkEyetrackerSession
from exptools2.core import Session
from trial import ExtinctionTrial
import numpy as np
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
    
    def __init__(self, output_str, output_dir=None, settings_file="expsettings.yml"):
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
        
        # Experiment-specific parameters
        # Can be overridden by settings file
        if hasattr(self, 'settings') and 'experiment' in self.settings:
            self.n_trials = self.settings['experiment'].get('n_trials', 2)
            self.trial_duration = self.settings['experiment'].get('trial_duration', 17.0)
        else:
            self.n_trials = 2  # Default number of trials
        
    def create_trials(self):
        """Create trial list for the session."""
        self.trials = []
        
        for trial_nr in range(self.n_trials):
            # Define phases for each trial
            # Using instance variables for flexibility
            phase_durations = [1.0, 3.0, 1.0, 3.0, 4.0, 4.0, 1.0, 1.0]
            phase_names = ["context", "NS", "context", "CS", "CS_distress", "US", "context", "fixcross"]
            # Create trial
            trial = ExtinctionTrial(
                session=self,
                trial_nr=trial_nr,
                phase_durations=phase_durations,
                phase_names=phase_names
            )
            
            self.trials.append(trial)
    


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