"""
Created on Sun Jan 4th 12:00:00 2026

@author: Ralph Wientjens

Trial class for Episodic Extinction experiment.
"""

from exptools2.core import Trial
from psychopy import visual
from psychopy import sound
from psychopy.core import getTime
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
        #phase_durations = [4.0, 4.0, 4.0, 4.0, 1.0]
        phase_names = ["context", "NS", "context", "CS", "CS_distress", "US", "context", "fixcross"]

        super().__init__(
            session=session,
            trial_nr=trial_nr,
            phase_durations=phase_durations,
            phase_names=phase_names,
            timing=timing,
            load_next_during_phase=load_next_during_phase,
            verbose=verbose
        )

        # Set parameters dict
        self.parameters = parameters or {}

        # Stimulus directory
        stim_dir = os.path.join(os.path.dirname(__file__), "stimuli_files")

        # Images
        self.context_img = visual.ImageStim(
            self.session.win,
            image=os.path.join(stim_dir, "contexts", 'ContextA01.jpg'),
            size=(1024, 576)
        )
        self.NS_img = visual.ImageStim(
            self.session.win,
            image=os.path.join(stim_dir, "NS", 'A01_armchair01.jpg'),
            size=(300, 300)
        )
        self.CS_img = visual.ImageStim(
            self.session.win,
            image=os.path.join(stim_dir, "CS", '01_brush.jpg'),
            size=(300, 300)
        )
        self.US_img = visual.ImageStim(
            self.session.win,
            image=os.path.join(stim_dir, "US", 'negative_01_vomit.jpeg'),
            size=(300, 300)
        )

        # Sound
        self.US_sound = sound.Sound(os.path.join(stim_dir, "USsounds", 'negative_01_vomit.wav'))

        # Distress slider
        self.distress_slider = visual.Slider(
            win=self.session.win,
            ticks=(0, 1),
            granularity=0,
            labels=["not at all distressed", "very distressed"],
            pos=(0, -200),
            size=(900, 50)
        )
        self.slider_value = 9999  # Initial dummy value
        self.distress_slider.setValue(self.slider_value)
        self.slider_moved = False

        # Fixation cross
        self.fixation = visual.TextStim(self.session.win, text='+', height=50, color='black')

        self.last_phase = None

    def log_slider(self, value, phase_name=None):
        """Log the distress slider value to the session's global_log."""
        idx = self.session.global_log.shape[0]
        self.session.global_log.loc[idx, 'trial_nr'] = self.trial_nr
        self.session.global_log.loc[idx, 'onset'] = self.session.clock.getTime()
        self.session.global_log.loc[idx, 'event_type'] = 'distress_rating' if phase_name is None else phase_name
        self.session.global_log.loc[idx, 'phase'] = self.phase
        self.session.global_log.loc[idx, 'response'] = value
        self.session.global_log.loc[idx, 'nr_frames'] = self.session.nr_frames


    def on_phase_start(self, phase):
        """Called when a new phase starts."""
        self.phase_name = self.phase_names[phase]
        # Play US sound during US phase
        if self.phase_name == "US":
            self.US_sound.play()
            idx = self.session.global_log.shape[0]
            self.session.global_log.loc[idx, 'trial_nr'] = self.trial_nr
            self.session.global_log.loc[idx, 'onset'] = self.session.clock.getTime()
            self.session.global_log.loc[idx, 'event_type'] = 'US_onset'
            self.session.global_log.loc[idx, 'phase'] = self.phase
            self.session.global_log.loc[idx, 'nr_frames'] = self.session.nr_frames

        # # Log slider at start of distress phase
        # if self.phase_name == "CS_distress":
        #     rating = self.distress_slider.getRating() or self.slider_value
        #     self.log_slider(value=rating, phase_name='distress_start')


    def draw(self):
        """Draw the current phase."""
        if self.phase != self.last_phase:
            self.on_phase_start(self.phase)
            self.last_phase = self.phase

        # Draw stimuli based on phase
        if self.phase == 0:  # context
            self.context_img.draw()
        elif self.phase == 1:  # NS
            self.context_img.draw()
            self.NS_img.draw()
        elif self.phase == 2:  # context
            self.context_img.draw()
        elif self.phase == 3:  # CS
            self.context_img.draw()
            self.CS_img.draw()
        elif self.phase == 4:  # CS_distress
            self.context_img.draw()
            self.CS_img.draw()
            self.distress_slider.draw()
        elif self.phase == 5:  # US
            self.context_img.draw()
            self.US_img.draw()
        elif self.phase == 6:  # context
            self.context_img.draw()
        elif self.phase == 7:  # fixcross
            self.fixation.draw()

    def phase_end(self):
        """Called automatically when a phase ends."""
        # Log slider value at end of distress phase
        if self.phase == 4 or self.phase_name == "CS_distress":
            self.session.win.flip()  # make sure last mouse events are processed
            rating = self.distress_slider.getRating() 
            if rating is None:
                rating = self.slider_value  # use last known value if none selected
            print("Distress rating recorded. Rating is the following: ", self.distress_slider.getRating())
            self.log_slider(value=rating, phase_name='distress_end')

        self.last_phase = None  # reset for next phase

    def run(self):
        """Run the trial, ensuring phase_end is called."""
        self.last_phase = None

        for phase_dur in self.phase_durations:
            # log phase start
            self.session.win.callOnFlip(self.log_phase_info, phase=self.phase)

            # load next trial if needed
            if self.load_next_during_phase == self.phase:
                self.load_next_trial(phase_dur)

            # main phase loop
            if self.timing == 'seconds':
                self.session.timer.add(phase_dur)
                while self.session.timer.getTime() < 0 and not self.exit_phase and not self.exit_trial:
                    self.draw()
                    if self.draw_each_frame:
                        self.session.win.flip()
                        self.session.nr_frames += 1
                    self.get_events()
            else:
                for _ in range(phase_dur):
                    if self.exit_phase or self.exit_trial:
                        break
                    self.draw()
                    self.session.win.flip()
                    self.get_events()
                    self.session.nr_frames += 1

            # ✅ Call your custom phase_end here
            self.phase_end()

            # reset exit_phase
            if self.exit_phase:
                self.session.timer.reset()
                self.exit_phase = False

            if self.exit_trial:
                self.session.timer.reset()
                break

            self.phase += 1

    # def get_events(self):
    #     """Get keyboard/mouse events."""
    #     events = super().get_events()
    #     if self.phase == 4:
    #         for ev in events:
    #             if ev.type == 'slider':
    #                 self.slider_value = self.distress_slider.getRating()
    #                 self.slider_moved = True

    #     return events
        # # Process events if needed
        # if self.phase == 4:  # Distress rating phase
        #     mouse = self.session.win.getMouse()
        #     if mouse.getPressed()[0]:  # Left mouse button is pressed
        #         self.slider_moved = True
        #         mouse_pos = mouse.getPos()
        #         self.distress_slider.setValue(mouse_pos[0])  # Update slider value based on mouse x position
        
        # return events
