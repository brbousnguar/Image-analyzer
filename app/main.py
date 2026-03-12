from __future__ import annotations

from io import BytesIO

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, UnidentifiedImageError

from app.services.plants import DEFAULT_MODEL_KEY, get_analyzer, get_model_options

app = FastAPI(title="Image Analyzer")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    model_options = get_model_options()
    default_model = next(
        model for model in model_options if model.key == DEFAULT_MODEL_KEY
    )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "model_options": model_options,
            "default_model_key": DEFAULT_MODEL_KEY,
            "default_model": default_model,
        },
    )


@app.post("/api/analyze")
async def analyze_image(
    file: UploadFile = File(...), model_key: str = Form(DEFAULT_MODEL_KEY)
) -> dict:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    payload = await file.read()

    try:
        image = Image.open(BytesIO(payload)).convert("RGB")
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="Unsupported image format.") from exc

    try:
        result = get_analyzer(model_key).analyze(image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Model assets for '{model_key}' could not be loaded locally: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected model error for '{model_key}': {exc}",
        ) from exc

    return result.model_dump()
