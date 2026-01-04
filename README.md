# Episodic Extinction Experiment

Experiment code for physiological and fMRI experiment studying episodic extinction, based on exptools2.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/RalphWientjens/Episodic_extinction.git
cd Episodic_extinction
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the experiment with default parameters:
```bash
python main.py
```

Run with custom parameters:
```bash
python main.py --subject 001 --session 1 --run 1 --output-dir data
```

Run with a settings file:
```bash
python main.py --subject 001 --settings settings.json
```

### Command-line arguments:
- `--subject`: Subject ID (default: 'test')
- `--session`: Session number (default: 1)
- `--run`: Run number (default: 1)
- `--output-dir`: Output directory for data files (default: 'data')
- `--settings`: Path to settings file (optional)

## Structure

- `main.py`: Main script to run the experiment
- `session.py`: Session class managing the experimental session
- `trial.py`: Trial class defining individual trial behavior
- `settings.json`: Configuration file for experiment parameters
- `requirements.txt`: Python dependencies

## Files

### trial.py
Contains the `ExtinctionTrial` class that defines:
- Trial phases (fixation, stimulus, response)
- Visual stimuli presentation
- Event handling and response collection

### session.py
Contains the `ExtinctionSession` class that manages:
- Trial creation and sequencing
- Instructions display
- Experiment flow
- Data collection

### main.py
Entry point for running the experiment:
- Command-line argument parsing
- Session initialization
- Experiment execution

## Configuration

Edit `settings.json` to customize:
- Window properties (size, fullscreen, colors)
- Input devices (mouse, keyboard)
- MRI settings (if using scanner)
- Experiment parameters (number of trials, durations)

## Data Output

Data files are saved in the specified output directory with naming format:
```
sub-{SUBJECT}_ses-{SESSION}_run-{RUN}_{TIMESTAMP}
```
