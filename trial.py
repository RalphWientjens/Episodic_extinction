"""
Trial class for Episodic Extinction experiment.
"""

from exptools2.core import Trial
from psychopy.visual import TextStim
import numpy as np


class ExtinctionTrial(Trial):
    """
    Trial class for the Episodic Extinction experiment.
    
    This trial presents stimuli and records responses according to the
    experimental protocol.
    """
    
    def __init__(self, session, trial_nr, phase_durations, phase_names,
                 parameters=None, timing='seconds', load_next_during_phase=None,
                 verbose=True):
        """
        Initialize ExtinctionTrial.
        
        Parameters
        ----------
        session : Session object
            The session this trial belongs to
        trial_nr : int
            Trial number
        phase_durations : array_like
            Duration of each phase (in seconds or frames)
        phase_names : list
            Names of the phases
        parameters : dict, optional
            Additional parameters for this trial
        timing : str
            'seconds' or 'frames'
        load_next_during_phase : int, optional
            Phase during which to load the next trial
        verbose : bool
            Print trial information
        """
        super().__init__(session, trial_nr, phase_durations, phase_names,
                        parameters, timing, load_next_during_phase, verbose)
        
        self.parameters = parameters if parameters is not None else {}
        
        # Create visual stimuli
        self.fixation = TextStim(self.session.win, text='+', 
                                 height=0.5, color='white')
        
        if 'stimulus_text' in self.parameters:
            self.stimulus = TextStim(self.session.win, 
                                    text=self.parameters['stimulus_text'],
                                    height=0.3, color='white')
        else:
            self.stimulus = TextStim(self.session.win, text='Stimulus',
                                    height=0.3, color='white')
    
    def draw(self):
        """Draw the current phase of the trial."""
        phase = self.phase_names[self.current_phase_index]
        
        if phase == 'fixation':
            self.fixation.draw()
        elif phase == 'stimulus':
            self.stimulus.draw()
        elif phase == 'response':
            self.fixation.draw()
    
    def get_events(self):
        """Get keyboard/mouse events."""
        events = super().get_events()
        
        # Process events if needed
        for event in events:
            if event['event_type'] == 'key':
                # Handle key responses
                self.parameters['response'] = event['key']
                self.parameters['response_time'] = event['t']
        
        return events
