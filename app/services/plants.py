from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

from app.schemas import AnalysisResult, ModelOption, Prediction

TOP_K = 5
DEFAULT_MODEL_KEY = "flora_sense"


@dataclass(frozen=True)
class ModelSpec:
    key: str
    label: str
    repo_id: str
    domain: str
    summary: str
    approx_params: str
    processor_repo_id: str | None = None


MODEL_SPECS = (
    ModelSpec(
        key="flora_sense",
        label="FloraSense",
        repo_id="Sisigoks/FloraSense",
        domain="Plants and flowers",
        summary="Best default for broad plant species lookup with a plant-focused label space.",
        approx_params="~300M params",
    ),
    ModelSpec(
        key="plant_vit",
        label="Plant Identity ViT",
        repo_id="umutbozdag/plant-identity",
        domain="Houseplants and common ornamental plants",
        summary="Ungated ViT classifier with published safetensors weights for common indoor and ornamental plant species.",
        approx_params="85.8M params",
    ),
    ModelSpec(
        key="bird_526",
        label="Bird Species 526",
        repo_id="prithivMLmods/Bird-Species-Classifier-526",
        domain="Bird species",
        summary="Specialized bird classifier with a large species set for fauna comparisons.",
        approx_params="~93M params",
    ),
    ModelSpec(
        key="butterfly_moth",
        label="Butterfly and Moth Species",
        repo_id="Dima806/butterfly_moth_species_detection",
        domain="Butterflies and moths",
        summary="Useful when the photo is insect-heavy and close enough for wing pattern cues.",
        approx_params="~86M params",
    ),
    ModelSpec(
        key="animal_90",
        label="90 Animal Species",
        repo_id="maceythm/vit-90-animals",
        domain="General animal species",
        summary="Broad fauna baseline model for mammals and other common animal classes.",
        approx_params="~86M params",
    ),
)
MODEL_REGISTRY = {spec.key: spec for spec in MODEL_SPECS}


class SpeciesAnalyzer:
    def __init__(self, spec: ModelSpec) -> None:
        self.spec = spec
        self.device = self._resolve_device()
        self.model = AutoModelForImageClassification.from_pretrained(spec.repo_id).to(
            self.device
        )
        self.processor = self._load_processor()
        self.model.eval()

    def analyze(self, image: Image.Image) -> AnalysisResult:
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.no_grad():
            logits = self.model(**inputs).logits

        probabilities = torch.softmax(logits, dim=-1)[0]
        topk = torch.topk(probabilities, k=min(TOP_K, probabilities.shape[-1]))

        predictions = [
            Prediction(
                label=self.model.config.id2label[index.item()],
                confidence=round(score.item(), 4),
            )
            for score, index in zip(topk.values, topk.indices)
        ]

        return AnalysisResult(
            model_name=self.spec.label,
            model_id=self.spec.repo_id,
            model_domain=self.spec.domain,
            predictions=predictions,
        )

    @staticmethod
    def _resolve_device() -> str:
        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def _load_processor(self):
        try:
            return AutoImageProcessor.from_pretrained(self.spec.repo_id)
        except OSError:
            fallback_repo_id = self.spec.processor_repo_id or getattr(
                self.model.config, "_name_or_path", None
            )
            if not fallback_repo_id:
                raise

            return AutoImageProcessor.from_pretrained(fallback_repo_id)


def get_model_spec(model_key: str) -> ModelSpec:
    spec = MODEL_REGISTRY.get(model_key)
    if spec is None:
        raise ValueError(f"Unknown model key: {model_key}")
    return spec


def get_model_options() -> list[ModelOption]:
    return [
        ModelOption(
            key=spec.key,
            label=spec.label,
            repo_id=spec.repo_id,
            domain=spec.domain,
            summary=spec.summary,
            approx_params=spec.approx_params,
        )
        for spec in MODEL_SPECS
    ]


@lru_cache(maxsize=len(MODEL_SPECS))
def get_analyzer(model_key: str = DEFAULT_MODEL_KEY) -> SpeciesAnalyzer:
    return SpeciesAnalyzer(get_model_spec(model_key))
