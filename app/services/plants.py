from __future__ import annotations

from functools import lru_cache

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

from app.schemas import AnalysisResult, Prediction

MODEL_ID = "juppy44/plant-identification-2m-vit-b"
TOP_K = 5


class PlantAnalyzer:
    def __init__(self) -> None:
        self.device = self._resolve_device()
        self.processor = AutoImageProcessor.from_pretrained(MODEL_ID)
        self.model = AutoModelForImageClassification.from_pretrained(MODEL_ID).to(
            self.device
        )
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
            model_id=MODEL_ID,
            predictions=predictions,
        )

    @staticmethod
    def _resolve_device() -> str:
        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"


@lru_cache(maxsize=1)
def get_analyzer() -> PlantAnalyzer:
    return PlantAnalyzer()
