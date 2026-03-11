from pydantic import BaseModel


class Prediction(BaseModel):
    label: str
    confidence: float


class AnalysisResult(BaseModel):
    model_id: str
    predictions: list[Prediction]
