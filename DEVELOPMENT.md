# Episodic Extinction Experiment - Development Guide

## Overview

This experiment is built using the exptools2 framework, which provides a structured approach for creating psychological and neuroscience experiments in Python with PsychoPy.

## Architecture

The experiment follows a three-tier structure:

1. **Trial** (`trial.py`): Defines what happens during a single trial
2. **Session** (`session.py`): Manages a sequence of trials and overall experiment flow
3. **Main** (`main.py`): Entry point for running the experiment with command-line arguments

## Extending the Experiment

### Adding New Trial Types

To create a new trial type, extend the `ExtinctionTrial` class in `trial.py`:

```python
class CustomTrial(ExtinctionTrial):
    def __init__(self, session, trial_nr, phase_durations, phase_names, **kwargs):
        super().__init__(session, trial_nr, phase_durations, phase_names, **kwargs)
        # Add custom initialization
        
    def draw(self):
        # Custom drawing logic
        pass
```

### Modifying Trial Phases

Trial phases are defined by:
- `phase_durations`: List of durations for each phase
- `phase_names`: List of names for each phase

Example:
```python
phase_durations = [0.5, 1.0, 0.5, 2.0]  # seconds
phase_names = ['fixation', 'cue', 'stimulus', 'response']
```

### Adding Stimuli

Create new stimuli in the trial's `__init__` method:

```python
from psychopy.visual import ImageStim, Circle

class ExtinctionTrial(Trial):
    def __init__(self, ...):
        super().__init__(...)
        
        # Add image stimulus
        self.image = ImageStim(self.session.win, image='path/to/image.png')
        
        # Add geometric shapes
        self.circle = Circle(self.session.win, radius=0.1, fillColor='red')
```

### Customizing Session Behavior

Modify the `ExtinctionSession` class in `session.py` to:

1. **Change trial sequence**:
```python
def create_trials(self):
    # Create custom trial sequence
    for condition in ['A', 'B', 'C']:
        for repetition in range(5):
            trial = ExtinctionTrial(...)
            self.trials.append(trial)
```

2. **Add practice trials**:
```python
def run(self):
    self.display_instructions()
    self.run_practice_trials()
    self.create_trials()
    self.start_experiment()
    for trial in self.trials:
        trial.run()
    self.close()
```

3. **Collect additional data**:
```python
def save_trial_data(self, trial):
    # Custom data saving logic
    pass
```

## Settings Configuration

The `settings.json` file controls experiment parameters. Key sections:

- **window**: Display settings (size, fullscreen, color)
- **mouse**: Mouse visibility
- **eyetracker**: Eye-tracking configuration
- **mri**: MRI scanner settings (trigger key, TR)
- **keys**: Keyboard mappings
- **experiment**: Trial timing and counts

## Data Output

Data is automatically saved by exptools2 in the format:
- `sub-{SUBJECT}_ses-{SESSION}_run-{RUN}_{TIMESTAMP}.tsv` - Event data
- `sub-{SUBJECT}_ses-{SESSION}_run-{RUN}_{TIMESTAMP}.log` - Log file

## Best Practices

1. **Keep trials modular**: Each trial should be self-contained
2. **Use parameters**: Pass trial-specific information via the `parameters` dict
3. **Test incrementally**: Run with small trial counts during development
4. **Use descriptive phase names**: Makes debugging easier
5. **Document changes**: Update this file when adding new features

## Testing

Test the experiment structure without running the full experiment:

```bash
# Quick test run
python main.py --subject test --session 0 --run 0

# Test with custom settings
python main.py --subject test --settings settings.json
```

## Common Tasks

### Change number of trials
Edit `session.py`:
```python
self.n_trials = 20  # Change from default 10
```

### Adjust trial timing
Edit `session.py` in `create_trials()`:
```python
phase_durations = [1.0, 2.0, 1.0]  # longer durations
```

### Add keyboard responses
Trial class automatically collects keyboard events. Access in `get_events()`:
```python
def get_events(self):
    events = super().get_events()
    for event in events:
        if event['event_type'] == 'key':
            print(f"Key pressed: {event['key']}")
```

## Next Steps

Future additions to this experiment structure:
- Eye-tracking integration
- MRI trigger synchronization
- Custom stimulus conditions
- Advanced response collection
- Data analysis scripts
