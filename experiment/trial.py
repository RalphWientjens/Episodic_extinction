"""
Created on Sun Jan 4th 12:00:00 2026

@author: Ralph Wientjens

Trial class for Episodic Extinction experiment.
"""

from exptools2.core import Trial
from psychopy import visual
from psychopy import sound
import numpy as np
import os


class ExtinctionTrial(Trial):
    """
    Trial class for the Episodic Extinction experiment.
    
    This trial presents four stimuli and records distress responses.
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
        phase_durations = [4.0, 4.0, 4.0, 4.0, 1.0]
        phase_names = ["context", "NS", "CS_distress", "US", "fixcross" ]

        super().__init__(session = session, trial_nr = trial_nr, phase_durations = phase_durations, phase_names = phase_names)
                        # parameters = {}, timing = "seconds", load_next_during_phase = None, verbose = True)
        
        # self.parameters = parameters if parameters is not None else {}

        # stim location
        stim_dir = os.path.join(
            os.path.dirname(__file__),
            "stimuli_files")

        #create stimuli:
        self.context_img = visual.ImageStim(self.session.win, 
                                            image=os.path.join(stim_dir, "contexts", 'ContextA01.jpg'),
                                            size=(1024, 576))
        
        self.NS_img = visual.ImageStim(self.session.win, 
                                       image=os.path.join(stim_dir, "NS", 'A01_armchair01.jpg'),
                                       size=(300, 300))
        
        self.CS_img = visual.ImageStim(self.session.win, 
                                                image=os.path.join(stim_dir, "CS", '01_brush.jpg'),
                                                size=(300, 300))
        
        #distress slider
        self.distress_slider = visual.Slider(
            win=session.win,
            ticks=(0, 1),
            granularity=0,
            labels=["not at all distressed", "very distressed"],
            pos=(0, -200),
            size=(900, 50))
        
        self.US_img = visual.ImageStim(self.session.win, 
                                       image=os.path.join(stim_dir, "US", 'negative_01_vomit.jpeg'),
                                       size=(300, 300))
        
        #sound
        # self.US_sound = sound.Sound(os.path.join(stim_dir, "USsounds", 'negative_01_vomit.wav'))
        
        # fixcross for ITI
        self.fixation = visual.TextStim(self.session.win, text='+', 
                                 height=0.1, color='black')     
    
    def draw(self):
        """Draw the current phase of the trial."""
    
        if self.phase == 0:
            self.context_img.draw()
        elif self.phase == 1:
            self.NS_img.draw()
        elif self.phase == 2:
            self.CS_img.draw()
            self.distress_slider.draw()
        elif self.phase == 3:
            self.US_img.draw()
            # self.US_sound.play()
        elif self.phase == 4:
            self.fixation.draw()
    

    def phase_end(self):
        """Called automatically when a phase ends.""" 

        # Log slider at the end of the CS phase
        if self.phase == 2:
            rating = self.distress_slider.getRating()

            if rating is None:
                rating = 0.5

            self.log_event(
                event_type="distress_rating",
                value=rating
            )

        super().phase_end()

    # def get_events(self):
    #     """Get keyboard/mouse events."""
    #     events = super().get_events()
        
    #     # Process events if needed
    #     for event in events:
    #         if event['event_type'] == 'key':
    #             # Handle key responses
    #             self.parameters['response'] = event['key']
    #             self.parameters['response_time'] = event['t']
        
    #     return events
