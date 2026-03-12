# Image Analyzer

Minimal Python webapp for local flora and fauna image classification with selectable Hugging Face models.

## What it does

- Upload an image from the browser
- Paste an image from the clipboard
- Switch between multiple local Hugging Face models
- Return the top predicted species candidates
- Show confidence scores for each prediction

## Stack

- FastAPI for the web server
- Jinja2 template for a simple upload UI
- Hugging Face `transformers`
- PyTorch with Apple Silicon `mps` support when available

## Included models

All models are downloaded from Hugging Face and executed locally through `transformers` and PyTorch.

- `Sisigoks/FloraSense` for broad plant and flower identification
- `umutbozdag/plant-identity` for common ornamental and houseplant classification with a ViT backbone
- `prithivMLmods/Bird-Species-Classifier-526` for bird species
- `Dima806/butterfly_moth_species_detection` for butterflies and moths
- `maceythm/vit-90-animals` for general animal species

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

- The first request for each model will take time because the weights need to download and load.
- If `mps` hits an unsupported op, PyTorch can fall back to CPU with `PYTORCH_ENABLE_MPS_FALLBACK=1`.
- The smaller ViT and DeiT style models in this app are a practical fit for 24 GB unified memory on Apple Silicon.
- These models are domain-specific, so the best choice depends on the image:
  - plants: `FloraSense` or `plant-identity`
  - birds: `Bird-Species-Classifier-526`
  - butterflies and moths: `butterfly_moth_species_detection`
  - broader animals: `vit-90-animals`
- Treat the result as a ranked shortlist, especially for visually similar species.
