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

- [`Sisigoks/FloraSense`](https://huggingface.co/Sisigoks/FloraSense) for broad plant and flower identification
- [`umutbozdag/plant-identity`](https://huggingface.co/umutbozdag/plant-identity) for common ornamental and houseplant classification with a ViT backbone
- [`prithivMLmods/Bird-Species-Classifier-526`](https://huggingface.co/prithivMLmods/Bird-Species-Classifier-526) for bird species
- [`Dima806/butterfly_moth_species_detection`](https://huggingface.co/Dima806/butterfly_moth_species_detection) for butterflies and moths
- [`maceythm/vit-90-animals`](https://huggingface.co/maceythm/vit-90-animals) for general animal species

## How Hugging Face models are loaded and used

The app uses `transformers` to pull each image classification model directly from Hugging Face and run it locally. This is the same pattern used in [app/services/plants.py](/Users/brbousnguar/Documents/Projects/Image-analyzer/app/services/plants.py).

```python
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

repo_id = "Sisigoks/FloraSense"
repo_url = f"https://huggingface.co/{repo_id}"
device = "mps" if torch.backends.mps.is_available() else "cpu"

# Download the model and processor from Hugging Face
model = AutoModelForImageClassification.from_pretrained(repo_id).to(device)
processor = AutoImageProcessor.from_pretrained(repo_id)
model.eval()

print(f"Loaded model from {repo_url}")

# Run inference on a local image
image = Image.open("example.jpg").convert("RGB")
inputs = processor(images=image, return_tensors="pt")
inputs = {key: value.to(device) for key, value in inputs.items()}

with torch.no_grad():
    logits = model(**inputs).logits

probabilities = torch.softmax(logits, dim=-1)[0]
topk = torch.topk(probabilities, k=5)

for score, index in zip(topk.values, topk.indices):
    label = model.config.id2label[index.item()]
    print(label, round(score.item(), 4))
```

In this project, the same loading flow is wrapped in `SpeciesAnalyzer`, and models are selected by repo ID such as:

```python
self.model = AutoModelForImageClassification.from_pretrained(spec.repo_id).to(
    self.device
)
self.processor = AutoImageProcessor.from_pretrained(spec.repo_id)
```

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
