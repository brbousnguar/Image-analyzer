# Image Analyzer

Minimal Python webapp for local plant species identification with `Sisigoks/FloraSense`.

## What it does

- Upload an image from the browser
- Return the top predicted plant species
- Show confidence scores for each prediction

## Stack

- FastAPI for the web server
- Jinja2 template for a simple upload UI
- Hugging Face `transformers`
- PyTorch with Apple Silicon `mps` support when available

## Model Choice

This app uses `Sisigoks/FloraSense`, a public Hugging Face image classification model for plant identification. It can be downloaded and run locally without gated-access approval.

Model page:

- https://huggingface.co/Sisigoks/FloraSense

## Project structure

```text
app/
  main.py
  config.py
  schemas.py
  services/plants.py
  static/
  templates/
requirements.txt
```

## Setup

Use Python 3.11 or 3.12. Python 3.14 is too new for a lot of ML packages and can break installs.

Create and activate a virtual environment, then install dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you only have Python 3.14 installed, install 3.12 first with your preferred tool (`pyenv`, Homebrew, or python.org).

## Run

```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
uvicorn app.main:app --reload
```

If you already installed dependencies with an older `transformers` version, upgrade inside the active virtual environment:

```bash
pip install -U transformers==4.56.1
```

Open `http://127.0.0.1:8000`.

## Notes for a 24 GB MacBook Pro

- `Florence-2-base-ft` is a reasonable local starting point.
- The first request will take time because the model weights need to load.
- If `mps` hits an unsupported op, PyTorch can fall back to CPU with `PYTORCH_ENABLE_MPS_FALLBACK=1`.
- This model predicts candidate species names only from the image. Accuracy will improve if the photo clearly shows leaves, flowers, fruit, bark, or the whole plant.
- Treat the result as a ranked shortlist, especially for very similar species such as close tree varieties.
