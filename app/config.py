from pydantic import BaseModel


class Settings(BaseModel):
    model_id: str = "florence-community/Florence-2-base-ft"
    max_new_tokens: int = 512
    device: str = "auto"


settings = Settings()
