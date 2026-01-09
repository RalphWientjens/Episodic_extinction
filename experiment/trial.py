"""
Created on Sun Jan 4th 12:00:00 2026

@author: Ralph Wientjens

Trial class for Episodic Extinction experiment.
"""

from exptools2.core import Trial
from psychopy import visual
from psychopy import sound
from psychopy.core import getTime
from psychopy.event import Mouse
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
        phase_names = ["context", "NS", "context", "CS", "CS_distress", "US", "context", "coherence", "fixcross"]

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
        self.context = self.parameters["context"]
        self.NS = self.parameters["NS"]
        self.CS = self.parameters["CS"]
        self.US = self.parameters["US_image"]
        self.US_sound_file = self.parameters["US_sound"]

        # Images
        self.context_img = visual.ImageStim(
            self.session.win,
            image=os.path.join(stim_dir, "contexts", self.context),
            size=self.session.settings["window"]["size"]
        )
        self.NS_img = visual.ImageStim(
            self.session.win,
            image=os.path.join(stim_dir, "NS", self.NS),
            size=(300, 300)
        )
        self.CS_img = visual.ImageStim(
            self.session.win,
            image=os.path.join(stim_dir, "CS", self.CS),
            size=(300, 300)
        )
        self.US_img = visual.ImageStim(
            self.session.win,
            image=os.path.join(stim_dir, "US", self.US),
            size=(300, 300)
        )

        # Fixation cross
        self.fixation = visual.TextStim(self.session.win, text='+', height=50, color='black')

        # Sound
        self.US_sound = sound.Sound(os.path.join(stim_dir, "USsounds", self.US_sound_file))

        # Define sliders
        # Distress slider
        distress_pos = (0, -self.session.settings["window"]["size"][1]//2 + 100)
        coherence_pos = (0, 0)

        self.distress_box = visual.Rect(
            self.session.win,
            width=1100,
            height=150,
            lineColor='black',
            fillColor='white',
            pos=(distress_pos)
        )

        self.distress_text = visual.TextStim(
            self.session.win, 
            text='How distressed do you feel?', 
            height=24, 
            color='black',
            pos=(distress_pos[0], distress_pos[1]+60)
        )

        self.distress_slider = visual.Slider(
            win=self.session.win,
            ticks=(0, 100),
            granularity=0,
            style='rating',
            labels=["not at all distressed", "very distressed"],
            labelHeight=20,
            pos=(distress_pos),
            size=(900, 50),
            labelColor="black",
            lineColor="black",
        )
        self.distress_value = None  # Initial dummy value
        self.distress_slider.setValue(self.distress_value)
        self.distress_started = False
        # self.slider_moved = False

        # Coherence slider
        self.coherence_box = visual.Rect(
            self.session.win,
            width=1100,
            height=150,
            lineColor='black',
            fillColor='white',
            pos=(coherence_pos)
        )
        self.coherence_text = visual.TextStim(
            self.session.win, 
            text='How coherent was your story?', 
            height=24, 
            color='black',
            pos=(coherence_pos[0], coherence_pos[1]+60)
        )
        self.coherence_slider = visual.Slider(
            win=self.session.win,
            ticks=(0, 100),
            granularity=0,
            style='rating',
            labels=["not at all coherent", "very coherent"],
            labelHeight=20,
            pos=(coherence_pos),
            size=(900, 50),
            labelColor="black",
            lineColor="black",
        )
        self.coherence_value = None  # Initial dummy value
        self.coherence_slider.setValue(self.coherence_value)
        self.coherence_started = False

        self.last_phase = None

    # For logging slider values, used in on_phase_end
    def log_slider(self, value, phase_name=None):
        """Log the distress slider value to the session's global_log."""
        idx = self.session.global_log.shape[0]
        self.session.global_log.loc[idx, 'trial_nr'] = self.trial_nr
        self.session.global_log.loc[idx, 'onset'] = self.session.clock.getTime()
        self.session.global_log.loc[idx, 'event_type'] = 'distress_rating' if phase_name is None else phase_name
        self.session.global_log.loc[idx, 'phase'] = self.phase
        self.session.global_log.loc[idx, 'response'] = value
        self.session.global_log.loc[idx, 'nr_frames'] = self.session.nr_frames
    
    #For stimulus logging, unnecessary at the moment, can be used in on_phase_start
    def stim_log(self, stimulus):
        """Log stimulus presentation to the session's global_log."""
        idx = self.session.global_log.shape[0]
        self.session.global_log.loc[idx, 'trial_nr'] = self.trial_nr
        self.session.global_log.loc[idx, 'onset'] = self.session.clock.getTime()
        self.session.global_log.loc[idx, 'event_type'] = self.phase_name + "_stim"
        self.session.global_log.loc[idx, 'phase'] = self.phase
        self.session.global_log.loc[idx, 'stimulus'] = stimulus
        self.session.global_log.loc[idx, 'nr_frames'] = self.session.nr_frames


    def on_phase_start(self, phase):
        """Called when a new phase starts."""
        self.phase_name = self.phase_names[self.phase]

        if self.phase_name == "CS_distress":
            # Reset slider
            self.distress_slider.reset()
            # Warp mouse to slider position
            self.session.mouse.setPos(self.distress_slider.pos)

        # Play US sound during US phase
        elif self.phase_name == "US":
            self.US_sound.play()

        elif self.phase_name == "coherence":
            # Reset slider
            self.coherence_slider.reset()
            # Warp mouse to slider position
            self.session.mouse.setPos(self.coherence_slider.pos)


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
            self.distress_box.draw()
            self.distress_text.draw()
            self.distress_slider.draw()
            buttons = self.session.mouse.getPressed()
            # BEFORE first click → keep mouse centered
            if not self.distress_started:
                self.session.mouse.setPos(self.distress_slider.pos)
            # FIRST click → allow normal slider behavior
            if buttons[0] and not self.distress_started:
                self.distress_started = True

        elif self.phase == 5:  # US
            self.context_img.draw()
            self.US_img.draw()

        elif self.phase == 6:  # context
            self.context_img.draw()

        elif self.phase == 7:  # Coherence
            self.coherence_box.draw()
            self.coherence_text.draw()
            self.coherence_slider.draw()
            buttons = self.session.mouse.getPressed()
            # BEFORE first click → keep mouse centered
            if not self.coherence_started:
                self.session.mouse.setPos(self.coherence_slider.pos)
            # FIRST click → allow normal slider behavior
            if buttons[0] and not self.coherence_started:
                self.coherence_started = True

        elif self.phase == 8:  # fixcross
            self.fixation.draw()

    def on_phase_end(self):
        """Called automatically when a phase ends. For fMRI experiment: change slider values to joystick input"""
        # Log slider value at end of distress phase
        if self.phase == 4:  # CS_distress
            self.session.win.flip()  # make sure last mouse events are processed
            distress_rating = self.distress_slider.getRating() 
            if distress_rating is None:
                distress_rating = self.distress_value  # use last known value if none selected
            print("Distress rating recorded. Rating is the following: ", self.distress_slider.getRating())
            self.log_slider(value=distress_rating, phase_name='distress_end')

        elif self.phase == 7:  # Coherence
            self.session.win.flip()  # make sure last mouse events are processed
            coherence_rating = self.coherence_slider.getRating() 
            if coherence_rating is None:
                coherence_rating = self.coherence_value  # use last known value if none selected
            print("Coherence rating recorded. Rating is the following: ", self.coherence_slider.getRating())
            self.log_slider(value=coherence_rating, phase_name='coherence_end')

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

            # Call custom phase_end
            self.on_phase_end()

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
