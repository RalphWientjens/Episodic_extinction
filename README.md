# Episodic Extinction (EE) Experiment

PsychoPy / exptools2 experiment code for an **Episodic Extinction** paradigm. The task presents sequences (“episodes”) consisting of visual scenes and sounds, interleaved with rating phases (distress and story coherence). The experiment is intended to be run across **multiple sessions (day 1–3)** with different trial structures per session.

> **Sidenote (stimulus files):** the repository expects a stimulus folder structure on disk (images + sounds). If you don’t have the stimulus set, **ask the repository owner** for the stimulus files before attempting to run the experiment.

---

## What the experiment entails

At a high level, trials are built from multiple **phases** (e.g., context → NS → context → CS → distress rating → US → …). Phase timing and the actual structure depend on the **session/day** and the **condition**.

### Common phase types

- **context**: background scene (full-screen image).
- **NS**: narrative stimulus overlay (image).
- **CS / CS_only**: conditioned stimulus image (with or without context, depending on session).
- **US / US_only**: unconditioned stimulus image (with optional associated sound).
- **CS_distress / CS_distress_only**: distress rating phase using a slider.
- **coherence**: coherence rating phase using a slider.
- **fixcross / fixcross_long**: fixation cross between trials/blocks (short vs long duration; both draw the same fixation, but have different timing rules).

Session-specific trial structures are defined in `SESSION_CONFIG` and per-phase durations are defined in `PHASES` (see `session.py`).

---

## Repository structure

### `main.py`
Entry point that parses command-line arguments and starts the session.

- Expects arguments:  
  1) `subject`  
  2) `sess` (session/day number)  
  3) `version` (stimset version string used to load the correct `.tsv`)

It creates the output directory and instantiates `ExtinctionSession`, then calls `ts.run()`.

### `session.py`
Defines the session logic and trial generation.

Key contents:
- `PHASES`: mapping from phase keys to `(draw_name, duration)`.  
  Example:  
  - `fixcross_long` maps to draw name `"fixcross"` with a longer random duration.
- `SESSION_CONFIG`: per-session phase-sequence templates (e.g., session 1 base trial structure).
- `resolve_condition_label(sess, condition)`: maps numerical condition values to labels used in `SESSION_CONFIG`.
- `pseudorandomize_stimset(...)`: shuffles a stimset while respecting constraints (no long repeats of condition/valence).
- `ExtinctionSession`:
  - loads **instructions** from `instructions.yml`
  - loads **practice stimset** and **main stimset** (`.tsv`)
  - builds practice trials and block-based main trials
  - shows instruction screens and runs trials

### `trial.py`
Defines the actual trial rendering and response collection.

Key responsibilities:
- Preloads stimuli (images + sounds) based on the row in the stimset.
- Implements:
  - `on_phase_start(...)`: resets sliders, plays US sound, etc.
  - `draw()`: draws the correct stimuli for the current phase
  - `on_phase_end()`: logs distress/coherence ratings
  - `run()`: iterates through the phase list and controls execution

> Note: phase timing depends on the timer logic in `run()`; ensure the phase timing mechanism matches PsychoPy/exptools2 expectations in your environment.

### `instructions.yml`
Text shown to participants. Organized by session:
- `session_1`, `session_2`, `session_3`
- keys like:
  - `before_session`
  - `practice_start` / `practice_end` (session 1)
  - `between_blocks`

Formatting uses YAML block scalars (`|`) to preserve line breaks. Placeholders like `{block}` are used for formatting between-block messages.

### `expsettings.yml`
Experiment settings (window, monitor, preferences, etc.), loaded by exptools2.

Notable fields:
- `window.size`, `window.fullscr`, `window.waitBlanking`
- `monitor.distance`, `monitor.width`

### Stimsets (`Stimsets/`)
The code expects stimsets at:

- `Stimsets/version{version}_day{sess}.tsv`

Example: if `version=1` and `sess=2`, it will look for:
- `Stimsets/version1_day2.tsv`

There is also a practice stimset expected at:
- `Practice_stimsets/day1_practice_stimset.tsv`

### Notebooks (e.g., `randomisation_EE.ipynb`)
Used to generate and/or validate stimsets and randomization logic. Not required for running the experiment, but useful for creating `Stimsets/*.tsv`.

---

## Stimulus files (required)

The experiment expects a stimulus directory called:

- `stimulus_files/` (relative to `trial.py`)

With subfolders such as (based on `trial.py`):
- `contexts_equalized/`
- `NS_equalized/`
- `CS_equalized/`
- `US_equalized/`
- `USsounds/`

Filenames are taken directly from the stimset `.tsv`, so they must match exactly.

If those folders/files are missing, the experiment will not run correctly. **Ask the owner for the stimulus set**.

---

## How to run

### 1) Create/activate a Python environment
This project depends on PsychoPy + exptools2 + standard scientific Python packages.

You can use the `exptools2_environment.yml` to install the environment I use or go to https://github.com/VU-Cog-Sci/exptools2 to see further instructions on how to install the environment

### 2) Run from the experiment folder
In the terminal, `cd` into the directory containing `main.py`, then run:

````bash
python [main.py](http://_vscodecontentref_/0) <subject> <sess> <version>