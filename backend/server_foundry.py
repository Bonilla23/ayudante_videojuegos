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

# Cargar base de datos limpia de Steam
DATASET_PATH = os.path.join(os.path.dirname(__file__), "../data/steam_clean.json")
try:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        STEAM_DB = json.load(f)
    print(f"Base de datos de Steam cargada con éxito: {len(STEAM_DB)} juegos en memoria.")
except Exception as e:
    STEAM_DB = []
    print(f"WARNING: No se pudo cargar la base de datos de Steam: {e}")

def buscar_candidatos_locales(juego_referencia: str, plataforma: str, limite: int = 5):
    # Buscar el juego de referencia en la base de datos
    ref_game = next(
        (g for g in STEAM_DB if juego_referencia.lower() in g["name"].lower()),
        None
    )
    
    # Filtrar por plataforma compatible
    candidatos = [g for g in STEAM_DB if plataforma in g["platforms"]]
    
    if ref_game:
        # Excluir el propio juego de entrada
        candidatos = [g for g in candidatos if g["name"].lower() != ref_game["name"].lower()]
        
        ref_genres = set(ref_game.get("genres", []))
        ref_cats = set(ref_game.get("categories", []))
        
        for cand in candidatos:
            cand_genres = set(cand.get("genres", []))
            cand_cats = set(cand.get("categories", []))
            
            # Puntuación por afinidad (coincidencia de géneros y categorías)
            genre_overlap = len(ref_genres.intersection(cand_genres))
            cat_overlap = len(ref_cats.intersection(cand_cats))
            
            cand["score"] = (genre_overlap * 3) + cat_overlap + (cand.get("rating", 0) / 10)
            
        candidatos.sort(key=lambda x: x.get("score", 0), reverse=True)
    else:
        # Fallback: ordenar por popularidad/rating si el juego no está en catálogo
        candidatos.sort(key=lambda x: x.get("rating", 0), reverse=True)
        
    return candidatos[:limite]


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
    output: Optional[str] = None # Nombre del juego
    motivo: Optional[str] = None # Razón
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

    # Debug: Ver qué llega al servidor
    print(f"DEBUG: Procesando '{request.input}' para {request.platform}")

    try:
        # Pre-filtrar candidatos en local
        candidatos = buscar_candidatos_locales(request.input, request.platform, limite=5)
        
        # Formatear el catálogo de contexto para el prompt
        catalogo_contexto = ""
        for idx, cand in enumerate(candidatos, 1):
            catalogo_contexto += f"{idx}. {cand['name']} | Géneros: {', '.join(cand['genres'])} | Puntuación: {cand['rating']}/10\n"
            
        messages = [
            {
                "role": "system", 
                "content": (
                    "Eres un experto recomendador de videojuegos.\n"
                    f"El usuario busca una recomendación compatible con {request.platform} basada en su gusto por '{request.input}'.\n\n"
                    "Debes elegir el mejor candidato ÚNICAMENTE de la siguiente lista de juegos reales en catálogo:\n"
                    f"{catalogo_contexto}\n"
                    "Instrucciones estrictas:\n"
                    "1. Selecciona el juego de la lista anterior que tenga mayor afinidad temática.\n"
                    "2. Responde estrictamente con un JSON con las claves:\n"
                    "   - 'juego': el nombre exacto del juego elegido.\n"
                    "   - 'motivo': una justificación breve e inteligente de por qué es ideal para él.\n"
                    "No recomiendes ningún juego que no esté explícitamente en la lista."
                )
            },
            {"role": "user", "content": request.input},
        ]
        
        resp, event = call_and_log(
            openai_client=client,
            deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=messages,
            log_path=LOG_PATH,
            group_id=GROUP_ID
        )
        
        # Intentar parsear la respuesta JSON del modelo
        content = resp.choices[0].message.content.strip()
        try:
            # Eliminar posibles markdowns de bloque de código si el modelo los pone
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            data = json.loads(content)
            juego = data.get("juego", "No encontrado")
            motivo = data.get("motivo", "No se proporcionó motivo")
        except:
            # Fallback si el modelo no devuelve JSON válido
            juego = content
            motivo = "No se pudo parsear el motivo del modelo."
        
        return {
            "ok": True,
            "output": juego,
            "motivo": motivo,
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
