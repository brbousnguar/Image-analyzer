from pydantic import BaseModel


class Prediction(BaseModel):
    label: str
    confidence: float


class AnalysisResult(BaseModel):
    model_name: str
    model_id: str
    model_url: str
    model_domain: str
    predictions: list[Prediction]


class ModelOption(BaseModel):
    key: str
    label: str
    repo_id: str
    repo_url: str
    domain: str
    summary: str
    approx_params: str
