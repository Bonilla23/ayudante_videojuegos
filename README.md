# Ayudante de Videojuegos

Este proyecto es un asistente inteligente que recomienda videojuegos basados en tus gustos (juegos que ya te gustan) y tu plataforma de escritorio (Windows, Mac o Linux), utilizando LLMs para ofrecer sugerencias personalizadas.

## Instrucciones
Para lanzar la demo localmente:
1. **Instalar dependencias:** `pip install fastapi uvicorn gradio requests` o `pip install -r requirements.txt`
3. **Lanzar Backend:** `python backend/server.py` (Se ejecuta en el puerto 8000)
4. **Lanzar UI:** `python ui/app.py` (Se ejecuta en el puerto 7860)

## Estructura del Repositorio
* `backend/`: Servidor API basado en FastAPI.
* `ui/`: Interfaz de usuario basada en Gradio.
* `tests/`: Casos de prueba iniciales (`smoke.jsonl`).
* `data/`: Documentación y archivos para el RAG (futuro).

## Configuración y Ejecución

### Variables de Entorno
Crea un archivo `.env` en la raíz:
```env
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
```
### Ejecución
**Backend:**
```bash
python backend/server.py
```

**UI:**
```bash
python ui/app.py
```

