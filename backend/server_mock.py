import os
import time
import uuid
import json
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Ayudante Videojuegos API (MOCK)")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "ok": False,
            "error": {
                "code": "INVALID_INPUT",
                "message": "Error de validación en los datos enviados.",
                "details": exc.errors()
            }
        },
    )

class PredictOptions(BaseModel):
    temperature: Optional[float] = Field(0.2, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(256, ge=1, le=600)

class PredictRequest(BaseModel):
    input: str = Field(..., min_length=1, max_length=1000)
    platform: Optional[str] = "Windows"
    options: Optional[PredictOptions] = PredictOptions()

    @validator("platform")
    def validate_platform(cls, v):
        allowed = ["Windows", "Linux", "Mac"]
        if v not in allowed:
            raise ValueError(f"Plataforma no soportada. Debe ser una de: {allowed}")
        return v

class PredictResponse(BaseModel):
    ok: bool
    output: Optional[str] = None # Nombre del juego
    motivo: Optional[str] = None # Razón de la recomendación
    meta: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    if not request.input.strip():
        return {
            "ok": False,
            "error": {
                "code": "INVALID_INPUT",
                "message": "El campo 'input' no puede estar vacío.",
                "details": {"field": "input"}
            }
        }

    # Implementación del Plan B con el nuevo contrato (Ejemplo: Skyrim)
    return {
        "ok": True,
        "output": "Dragon's Dogma",
        "motivo": f"Género RPG, categoría Open World y temática fantasía. Compatible con {request.platform}.",
        "meta": {
            "provider": "mock",
            "deployment": "Mock-Model-V3",
            "latency_ms": 10,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "request_id": str(uuid.uuid4())
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
