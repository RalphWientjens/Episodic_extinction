"""
Created on Sun Jan 4th 12:00:00 2026

@author: Ralph Wientjens

Trial class for Episodic Extinction experiment.
"""

from exptools2.core import Trial
from psychopy import visual
from psychopy import sound
from psychopy.core import getTime, Clock
import numpy as np
import os

class KeyboardScale:
    """
    A horizontally sliding scale driven entirely by keypresses.
    Replaces visual.Slider for button-box / fMRI contexts.

    Keys:
        left_key  – move marker left  (decrease value)
        right_key – move marker right (increase value)

    Parameters
    ----------
    win        : psychopy.visual.Window
    pos        : (x, y) centre of the scale
    width      : pixel width of the scale bar
    min_val    : minimum rating value  (default 0)
    max_val    : maximum rating value  (default 100)
    start_val  : initial marker position (default 50)
    step       : value change per keypress (default 2)
    label_left : text for the left anchor
    label_right: text for the right anchor
    question   : question text drawn above the scale
    left_key   : key name for leftward movement  (default 'left')
    right_key  : key name for rightward movement (default 'right')
    """

    def __init__(self, win, pos, width=900,
                 min_val=0, max_val=10, start_val=5, step=1,
                 label_left='', label_right='', question='',
                 left_key='left', right_key='right'):

        self.win = win
        self.pos = pos
        self.width = width
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.left_key = left_key
        self.right_key = right_key

        self.value = 999          # current rating
        self._display_val = start_val   # value currently shown by the marker (lags behind self.value until first keypress)
        self.activated = False
        self._start_val = start_val     # stored for reset()

        cx, cy = pos

        # ── Visual components ──────────────────────────────────────────

        # Background box
        self.box = visual.Rect(
            win, width=width + 200, height=160,
            lineColor='black', fillColor='white',
            pos=(cx, cy)
        )

        # Question text (above the bar)
        self.question_stim = visual.TextStim(
            win, text=question, height=24, color='black', font='Arial',
            pos=(cx, cy + 55), anchorHoriz='center'
        )

        # Horizontal bar
        self.bar = visual.Line(
            win,
            start=(cx - width / 2, cy),
            end=(cx + width / 2, cy),
            lineColor='black', lineWidth=3
        )

        # Tick marks at each end
        tick_h = 25
        self.tick_left = visual.Line(
            win,
            start=(cx - width / 2, cy - tick_h),
            end=(cx - width / 2, cy + tick_h),
            lineColor='black', lineWidth=5
        )
        self.tick_right = visual.Line(
            win,
            start=(cx + width / 2, cy - tick_h),
            end=(cx + width / 2, cy + tick_h),
            lineColor='black', lineWidth=5
        )

        # Marker (moveable circle)
        self.marker = visual.Circle(
            win, radius=25,
            fillColor = "grey", lineColor= "darkgrey",
            pos=self._val_to_pos(start_val)
        )

        # Anchor labels
        self.label_left_stim = visual.TextStim(
            win, text=label_left, height=20, color='black', font='Arial',
            pos=(cx - width / 2, cy - 35), anchorHoriz='center'
        )
        self.label_right_stim = visual.TextStim(
            win, text=label_right, height=20, color='black', font='Arial',
            pos=(cx + width / 2, cy - 35), anchorHoriz='center'
        )

        # Question text (above the bar)
        self.question_stim = visual.TextStim(
            win, text=question, height=24, color='black', font='Arial',
            pos=(cx, cy + 55), anchorHoriz='center'
        )

        # Numeric readout (below marker)
        self.readout_stim = visual.TextStim(
            win, text=str(int(start_val)), height=20, color='black', font='Arial',
            pos=(cx, cy - 60), anchorHoriz='center'
        )
        self.readout_stim.opacity = 0  # start invisible until first keypress

    # ── Helpers ───────────────────────────────────────────────────────

    def _val_to_pos(self, val):
        """Convert a 0-100 value to an x-pixel position on the bar."""
        cx, cy = self.pos
        proportion = (val - self.min_val) / (self.max_val - self.min_val)
        x = (cx - self.width / 2) + proportion * self.width
        return (x, cy)

    def reset(self, start_val=None):
        """Reset marker to start_val (or the original start_val if None)."""
        if start_val is not None:
            self._start_val = start_val
        self.value = 999
        self._display_val = self._start_val
        self.activated = False
        self.marker.fillColor = "grey"
        self.marker.lineColor = "darkgrey"
        self.readout_stim.opacity = 0  # hide readout until first keypress
        self._refresh_marker()

    def handle_key(self, key):
        """
        Process a single keypress.
        Call from get_events() with each key string received.
        Returns True if the key was consumed by this scale.
        """
        if key == self.left_key:
            if not self.activated:
                self.activated = True
                self.value = self._display_val  # set to start_val on first press, then move on subsequent presses
                self.marker.fillColor = "red"  # <- change color on first press
                self.marker.lineColor = "black"
                self.readout_stim.opacity = 1  # show readout on first keypress
            else:
                self._display_val = max(self.min_val, self.value - self.step)
                self.value = self._display_val
            self._refresh_marker()
            return True

        elif key == self.right_key:
            if not self.activated:
                self.activated = True
                self.value = self._display_val  # set to start_val on first press, then move on subsequent presses
                self.marker.fillColor = "red"  # <- change color on first press
                self.marker.lineColor = "black"
                self.readout_stim.opacity = 1  # show readout on first keypress
            else:
                self._display_val = min(self.max_val, self.value + self.step)
                self.value = self._display_val
            self._refresh_marker()
            return True
        return False

    def _refresh_marker(self):
        """Update marker position and numeric readout to match self.value."""
        self.marker.pos = self._val_to_pos(self._display_val)
        self.readout_stim.text = str(round(self._display_val, 1))

    def getRating(self):
        """Return current value (mirrors visual.Slider API)."""
        return self.value

    def draw(self):
        """Draw all scale components."""
        self.box.draw()
        self.question_stim.draw()
        self.bar.draw()
        self.tick_left.draw()
        self.tick_right.draw()
        self.label_left_stim.draw()
        self.label_right_stim.draw()
        self.marker.draw()
        self.readout_stim.draw()


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

        # ============================ STIMULI =======================================
        # Stimulus directory
        stim_dir = os.path.join(os.path.dirname(__file__), "stimulus_files")
        self.CS = self.parameters["CS"]
        self.US = self.parameters["US"]
        self.US_sound_file = self.parameters["US_sound"]

        if parameters.get('CS', ''):
            self.CS_img = visual.ImageStim(
                self.session.win,
                # image=os.path.join(stim_dir, "CS_equalized", self.CS),  #for equalized luminance images
                image=os.path.join(stim_dir, "CS", self.CS),
                size=(1000, 1000)
            )
        else:
            self.CS_img = None  # No CS for this trial

        self.US_img = visual.ImageStim(
            self.session.win,
            # image=os.path.join(stim_dir, "US_equalized", self.US), #for equalized luminance images
            image=os.path.join(stim_dir, "US", self.US),
            size=(1000, 1000)
        )

        # Fixation cross
        self.fixation = visual.TextStim(self.session.win, text='+', height=50, color='black', font="Arial")

        # Sound
        self.US_sound = sound.Sound(os.path.join(stim_dir, "USsounds", self.US_sound_file))

        # ============================ Use keyboard scales instead =======================================
        # Position: near the bottom of the screen for distress (shown over CS),
        # centred for coherence (shown alone during ITI).
        distress_pos  = (0, -self.session.settings["window"]["size"][1] // 2 - 20 - 50)
        coherence_pos = (0, 0)

        self.distress_scale = KeyboardScale(
            win=self.session.win,
            pos=distress_pos,
            width=900,
            min_val=0, max_val=10, start_val=5, step=1,
            label_left='Not at all distressed',
            label_right='Very distressed',
            question='How distressed do you feel?',
            left_key='left', right_key='right'       # ← change to '1'/'2' or 'b'/'y' for button box in fMRI
        )

        self.coherence_scale = KeyboardScale(
            win=self.session.win,
            pos=coherence_pos,
            width=900,
            min_val=0, max_val=10, start_val=5, step=1,
            label_left='Not at all coherent',
            label_right='Very coherent',
            question='How coherent was your story?',
            left_key='left', right_key='right'
        )
        # self.phase = None  # Initialize phase to avoid AttributeError
        # self.last_phase = None

        # Track which scale is active so get_events() knows where to route keys
        self._active_scale = None

        #Set blocks and properties per block if needed
        self.block = self.parameters['block']

    # =========================================================================
    # Logging helpers
    # =========================================================================

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

    #For stimulus logging, unnecessary at the moment, can be used in on_phase_start (for VAS value at phase start)
    def stim_log(self, stimulus):
        """Log stimulus presentation to the session's global_log."""
        idx = self.session.global_log.shape[0]
        self.session.global_log.loc[idx, 'trial_nr'] = self.trial_nr
        self.session.global_log.loc[idx, 'onset'] = self.session.clock.getTime()
        self.session.global_log.loc[idx, 'event_type'] = self.phase_name + "_stim"
        self.session.global_log.loc[idx, 'phase'] = self.phase
        self.session.global_log.loc[idx, 'stimulus'] = stimulus
        self.session.global_log.loc[idx, 'nr_frames'] = self.session.nr_frames

    # =========================================================================
    # Phase hooks
    # =========================================================================

    def on_phase_start(self, phase):
        """Called when a new phase starts."""
        if 0 <= self.phase < len(self.phase_names):
            self.phase_name = self.phase_names[self.phase]
        else:
            raise IndexError(f"Phase index {self.phase} is out of bounds for phase_names.")

        if self.phase_name == "CS_distress":
            self.distress_scale.reset()             # Marker reset to start_val (50)
            self._active_scale = self.distress_scale

        # Play US sound during US phase
        elif self.phase_name == "US":
            self.US_sound.play()
            self._active_scale = None  # No scale active during US presentation

        elif self.phase_name == "coherence":
            self.coherence_scale.reset()             # Marker reset to start_val (50)
            self._active_scale = self.coherence_scale

        else:
            self._active_scale = None

    def draw(self):
        """Called every frame by the run loop. Delegates to on_phase_start on
        the first frame of each phase, then draws the appropriate stimuli."""

        if self.last_phase is None or self.phase != self.last_phase:
            self.on_phase_start(self.phase)
            self.last_phase = self.phase

        # Draw stimuli per phase
        elif self.phase_name == "CS":  # CS
            self.CS_img.draw()
            self.fixation.draw()

        elif self.phase_name == "CS_distress":  # CS_distress
            self.CS_img.draw()
            self.fixation.draw()
            self.distress_scale.draw()

        elif self.phase_name == "US":  # US
            self.US_img.draw()
            self.fixation.draw()

        elif self.phase_name == "coherence":  # Coherence
            self.coherence_scale.draw()

        elif self.phase_name == "fixcross":  # fixcross
            self.fixation.draw()

    # =========================================================================
    # Event handling
    # =========================================================================

    def get_events(self):
        """
        Override the exptools2 get_events() so that during rating phases
        keypresses are forwarded to the active KeyboardScale.

        The super() call preserves all default exptools2 behaviour
        (quit-key detection, trigger logging, etc.) and returns a list of
        (key, timestamp) tuples that we can inspect afterwards.
        """
        events = super().get_events()

        # Route arrow keys (or button-box keys) to whichever scale is active
        if self._active_scale is not None:
            for key, t in events:
                self._active_scale.handle_key(key)

        return events

    # =========================================================================
    # Phase end
    # =========================================================================

    def on_phase_end(self):
        """
        Called automatically when a phase ends.
        Reads the final scale value and logs it.
        """
        self.phase_name = self.phase_names[self.phase]

        # Log slider value at end of distress phase
        if self.phase_name in ("CS_distress", "CS_distress_only"):
            distress_rating = self.distress_scale.getRating()
            print(f"Distress rating recorded: {distress_rating}")
            self.log_slider(value=distress_rating, phase_name='distress_value')

        # Log slider value at end of coherence phase
        elif self.phase_name == "coherence":
            coherence_rating = self.coherence_scale.getRating() #if self._active_scale == self.coherence_scale else 999
            print(f"Coherence rating recorded: {coherence_rating}")
            self.log_slider(value=coherence_rating, phase_name='coherence_value')

        # Deactivate scale and reset phase-tracking sentinel
        self._active_scale = None
        self.last_phase = None  # reset for next phase

    # =========================================================================
    # Run loop
    # =========================================================================

    def log_phase_info(self, phase=None):
        super().log_phase_info(phase)
        if self.eyetracker_on:  # send msg to eyetracker
            msg = f'trial {self.trial_nr} parameter episode_nr : {self.parameters["episode_nr"]}'
            self.session.tracker.sendMessage(msg)


    def run(self):
        """Run the trial, ensuring phase_end is called."""
        self.last_phase = None
        self.phase = 0
        self.exit_phase = False
        self.exit_trial = False

        # log trial start in session time
        print(f"Trial {self.trial_nr} starts at {self.session.clock.getTime():.3f}")

        trial_clock = Clock()
        trial_clock.reset()

        phase_start = 0.0

        useParallel = hasattr(self.session, "parallelPort")

        for phase_dur in self.phase_durations:

            # Log phase start ON FLIP, using SESSION time
            self.session.win.callOnFlip(
                self.log_phase_info,
                phase=self.phase
            )

            if hasattr(self.session, "serialPort"):
                self.session.win.callOnFlip(self.session.serialPort.write, bytearray([self.parameters["episode_nr"]]))

            if useParallel:
                self.session.win.callOnFlip(self.session.parallelPort.setData, self.parameters["episode_nr"])
                self.parallelPortStartFrame = 0 # log_phase_info sets session nr_frames to 0.

            # load next trial if needed
            if self.load_next_during_phase == self.phase:
                self.load_next_trial(phase_dur)

             # ---- PHASE LOOP (SECONDS MODE) ----
            if self.timing == 'seconds':

                while (
                    trial_clock.getTime() < phase_start + phase_dur
                    and not self.exit_phase
                    and not self.exit_trial
                ):
                    self.draw()
                    if self.draw_each_frame:
                        if useParallel and self.session.nr_frames == self.parallelPortStartFrame + 1:
                            self.session.win.callOnFlip(self.session.parallelPort.setData, 0)
                        self.session.win.flip()
                        self.session.nr_frames += 1
                    self.get_events()


            # ---- PHASE LOOP (FRAMES MODE) ----
            else:
                for _ in range(phase_dur):
                    if self.exit_phase or self.exit_trial:
                        break
                    self.draw()
                    self.session.win.flip()
                    self.get_events()
                    self.session.nr_frames += 1

            # Phase end hook
            self.on_phase_end()

            # reset exit_phase
            if self.exit_phase:
                self.exit_phase = False

            if self.exit_trial:
                break

            phase_start += phase_dur
            self.phase += 1