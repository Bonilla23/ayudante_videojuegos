import os
import time
import uuid
import json
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Ayudante Videojuegos API (Foundry)")

# Configuración
GROUP_ID = os.getenv("GROUP_ID", "G0")
LOG_PATH = os.getenv("LOG_PATH", "logs/logs.jsonl")

# Azure OpenAI Config
AZURE_OPENAI_BASE_URL = os.getenv("AZURE_OPENAI_BASE_URL")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "DeepSeek-V4-Flash")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

# Inicializar cliente OpenAI
if not AZURE_OPENAI_API_KEY or AZURE_OPENAI_API_KEY == "TU_API_KEY_AQUI":
    print("WARNING: AZURE_OPENAI_API_KEY no configurada correctamente.")

client = OpenAI(
    base_url=AZURE_OPENAI_BASE_URL,
    api_key=AZURE_OPENAI_API_KEY,
    default_headers={"api-key": AZURE_OPENAI_API_KEY},
)

def call_and_log(openai_client: OpenAI, deployment: str, messages, log_path: str, group_id: str, exercise_id: str = "P12-S2"):
    request_id = str(uuid.uuid4())
    t0 = time.time()

    resp = openai_client.chat.completions.create(
        model=deployment,
        messages=messages,
        max_tokens=600,
        temperature=0.2,
    )

    dt_ms = int((time.time() - t0) * 1000)
    u = resp.usage

    event = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "group_id": group_id,
        "exercise_id": exercise_id,
        "request_id": request_id,
        "deployment": deployment,
        "prompt_tokens": u.prompt_tokens,
        "completion_tokens": u.completion_tokens,
        "total_tokens": u.total_tokens,
        "latency_ms": dt_ms,
    }

    # Asegurar que el directorio de logs existe
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return resp, event

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
    output: Optional[str] = None
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

    try:
        messages = [
            {"role": "system", "content": f"Eres un asistente útil especializado en videojuegos para la plataforma {request.platform}."},
            {"role": "user", "content": request.input},
        ]
        
        resp, event = call_and_log(
            openai_client=client,
            deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=messages,
            log_path=LOG_PATH,
            group_id=GROUP_ID
        )
        
        return {
            "ok": True,
            "output": resp.choices[0].message.content,
            "meta": {
                "provider": "foundry",
                "deployment": AZURE_OPENAI_DEPLOYMENT_NAME,
                "latency_ms": event["latency_ms"],
                "prompt_tokens": event["prompt_tokens"],
                "completion_tokens": event["completion_tokens"],
                "total_tokens": event["total_tokens"],
                "request_id": event["request_id"]
            }
        }

    except Exception as e:
        return {
            "ok": False,
            "error": {
                "code": "PROVIDER_ERROR",
                "message": f"Error al procesar con Azure AI Foundry: {str(e)}",
                "details": {}
            }
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
