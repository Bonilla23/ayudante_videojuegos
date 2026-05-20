from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import time

app = FastAPI(title="Ayudante Videojuegos API")

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
    max_tokens: Optional[int] = Field(256, ge=1, le=2048)

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
    output: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    start_time = time.time()
    
    # Validación mínima
    if not request.input.strip():
        return {
            "ok": False,
            "error": {
                "code": "INVALID_INPUT",
                "message": "El campo 'input' no puede estar vacío.",
                "details": {"field": "input"}
            }
        }

    try:
        # Mock de respuesta de Azure/LLM
        # En el futuro, aquí se llamará al servicio de Azure
        mock_output = f"Basado en tus gustos sobre '{request.input}' para la plataforma {request.platform}, te recomiendo explorar titulos similares. Esta es una respuesta simulada (MOCK)."
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        return {
            "ok": True,
            "output": mock_output,
            "meta": {
                "model": "gpt-mock-v1",
                "latency_ms": latency_ms
            }
        }
    except Exception as e:
        return {
            "ok": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"Error interno en el servidor: {str(e)}",
                "details": {}
            }
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
