# Learned Lessons

## Context

While setting up the local Florence-2 image analyzer on macOS, the initial Python environment and dependency pins were not compatible with the current machine state.

## Issues Found

### 1. Invalid `torch` version pin

The original `requirements.txt` used:

```text
torch==2.8.0
```

That version was not available from PyPI in the current environment. The install error was:

```text
ERROR: Could not find a version that satisfies the requirement torch==2.8.0
```

### 2. Python 3.14 was too new for the ML stack

The virtual environment was created with Python `3.14.0`. That is a poor target for a local ML app because PyTorch and related packages often lag support for the newest Python release.

Symptoms:

- package resolution problems
- higher risk of runtime incompatibilities
- reduced confidence that Florence dependencies will install cleanly

### 3. `pyenv` was installed but shell shims were not active

The machine already had `pyenv` and Python `3.12.9` installed, but the shell was not initialized to expose `python` through `pyenv` shims.

Symptoms:

```text
pyenv local 3.12.9
python --version
zsh: command not found: python
```

## Fixes Applied

### Dependency fixes

`requirements.txt` was updated to use a currently available PyTorch version and include Florence runtime dependencies:

```text
torch==2.10.0
torchvision==0.25.0
timm>=1.0.16,<2.0.0
```

Reason:

- `torchvision` is commonly needed with vision pipelines
- `timm` is frequently required by Florence custom model code

### Python version fix

The project setup was changed to target Python `3.12` instead of Python `3.14`.

Working approach:

```bash
pyenv local 3.12.9
pyenv exec python -m venv .venv
source .venv/bin/activate
python --version
pip install -U pip
pip install -r requirements.txt
```

### Shell / `pyenv` workaround

Because the shell was not configured to expose `python` through `pyenv`, the immediate workaround was to use:

```bash
pyenv exec python -m venv .venv
```

This avoided needing to fix shell initialization before continuing.

## Root Cause Summary

The setup failed because of a combination of:

- an incorrect pinned `torch` version
- use of a too-new Python runtime for ML dependencies
- incomplete `pyenv` shell integration

Any one of these would create friction. Together they blocked environment setup.

## Recommended Practice For This Repo

- Use Python `3.12.x`
- Create the environment with `pyenv exec python -m venv .venv` if shell shims are not configured
- Keep `torch` pins aligned with versions actually published for the target Python version
- Expect Hugging Face vision models to need extra runtime packages like `torchvision` and `timm`
- On Apple Silicon, export `PYTORCH_ENABLE_MPS_FALLBACK=1` before running the app

## Optional Permanent Shell Fix

To make `python` resolve correctly through `pyenv` in future shells, add `pyenv` initialization to `~/.zshrc`.

## Current Known-Good Setup Pattern

```bash
cd /Users/brbousnguar/Documents/Projects/Image-analyzer
pyenv local 3.12.9
pyenv exec python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
export PYTORCH_ENABLE_MPS_FALLBACK=1
uvicorn app.main:app --reload
```
