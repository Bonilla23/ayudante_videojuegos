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

# Cargar base de datos limpia de Steam
DATASET_PATH = os.path.join(os.path.dirname(__file__), "../data/steam_clean.json")
try:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        STEAM_DB = json.load(f)
    print(f"Base de datos de Steam (MOCK) cargada con éxito: {len(STEAM_DB)} juegos en memoria.")
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
            
            # Puntuación por afinidad
            genre_overlap = len(ref_genres.intersection(cand_genres))
            cat_overlap = len(ref_cats.intersection(cand_cats))
            
            cand["score"] = (genre_overlap * 3) + cat_overlap + (cand.get("rating", 0) / 10)
            
        candidatos.sort(key=lambda x: x.get("score", 0), reverse=True)
    else:
        # Fallback si no está el juego en catálogo
        candidatos.sort(key=lambda x: x.get("rating", 0), reverse=True)
        
    return candidatos[:limite]


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

    # Buscar dinámicamente un candidato en el catálogo local para simular la lógica real
    candidatos = buscar_candidatos_locales(request.input, request.platform, limite=1)
    
    if candidatos:
        juego = candidatos[0]["name"]
        genres = ", ".join(candidatos[0].get("genres", ["Acción"]))
        cats = ", ".join(candidatos[0].get("categories", ["Single-player"])[:2])
        motivo = f"[MOCK] Género {genres}, categorías {cats}. Compatible con {request.platform}."
    else:
        # Fallback si no hay ningún candidato
        juego = "Half-Life 2"
        motivo = f"[MOCK] Género Acción, categoría Single-player. Compatible con {request.platform}."

    return {
        "ok": True,
        "output": juego,
        "motivo": motivo,
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
