# Ayudante de Videojuegos - Vertical Slice

Este proyecto es un asistente inteligente que recomienda videojuegos basados en tus gustos (juegos que ya te gustan) y tu plataforma de escritorio (Windows, Mac o Linux), utilizando LLMs para ofrecer sugerencias personalizadas.

## Instrucciones
Para lanzar la demo localmente:
1. **Instalar dependencias:** `pip install fastapi uvicorn gradio requests`
2. **Lanzar Backend:** `python backend/server.py` (Se ejecuta en el puerto 8000)
3. **Lanzar UI:** `python ui/app.py` (Se ejecuta en el puerto 7860)

## Estructura del Repositorio
* `backend/`: Servidor API basado en FastAPI.
* `ui/`: Interfaz de usuario basada en Gradio.
* `tests/`: Casos de prueba iniciales (`smoke.jsonl`).
* `data/`: Documentación y archivos para el RAG (futuro).
* `docs/`: Documentación del proyecto.

## Configuración y Ejecución

### Variables de Entorno
Crea un archivo `.env` en la raíz (opcional para Mock):
```env
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
```

### Instalación
```bash
pip install -r requirements.txt
```
*(Nota: Crea un `requirements.txt` con `fastapi`, `uvicorn`, `gradio`, `requests`)*

### Ejecución
**Backend:**
```bash
python backend/server.py
```

**UI:**
```bash
python ui/app.py
```
| Soy de Mac y me encantan los juegos de estrategia, ¿cual deberia comprar?    | JSON con output string     | Mock: Has preguntado... | Pase      |
| (Vacio)                                                                      | JSON Error "INVALID_INPUT" | Error (INVALID_INPUT)   | Pase      |
