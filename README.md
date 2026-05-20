# Ayudante de Videojuegos - Vertical Slice

Este proyecto es un asistente inteligente que recomienda videojuegos basados en tus gustos (juegos que ya te gustan) y tu plataforma de escritorio (Windows, Mac o Linux), utilizando LLMs para ofrecer sugerencias personalizadas.

## Checkpoint: Sesión 2 - Vertical Slice

### Link a la demo / Instrucciones
Para lanzar la demo localmente:
1. **Instalar dependencias:** `pip install fastapi uvicorn gradio requests`
2. **Lanzar Backend:** `python backend/server.py` (Se ejecuta en el puerto 8000)
3. **Lanzar UI:** `python ui/app.py` (Se ejecuta en el puerto 7860)

### Estado del Proyecto (3 Bullets)
* **Qué funciona:** Estructura de carpetas completa, contrato de API `POST /predict` estable con respuestas estructuradas (JSON), Interfaz de usuario en Gradio comunicada con backend, y sistema de Mocking operativo.
* **Qué falta:** Conexión real con Azure OpenAI Service (actualmente usa Mock), integración de base de datos RAG para documentos específicos.
* **Bloqueo principal:** Ninguno. Pendiente de configuración de credenciales de Azure.

### Plan para conectar Azure OpenAI
Para pasar del Mock a producción, se seguirán estos pasos:
1. **Recurso:** Crear un recurso de Azure OpenAI Service y desplegar un modelo (ej: `gpt-4o`).
2. **Variables de Entorno:**
   - `AZURE_OPENAI_API_KEY`: Clave de API del recurso.
   - `AZURE_OPENAI_ENDPOINT`: URL del endpoint (ej: `https://...openai.azure.com/`).
   - `AZURE_OPENAI_DEPLOYMENT_NAME`: Nombre del despliegue del modelo.
3. **Cambios en Código:**
   - Instalar `openai` library (`pip install openai`).
   - Sustituir la lógica de la función `predict` en `backend/server.py` por una llamada a `AzureOpenAI(api_key=..., api_version=..., azure_endpoint=...)`.
4. **Prueba:** Ejecutar `python backend/server.py` y verificar que el campo `meta.model` devuelva el nombre del modelo de Azure real.

---

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

## Evidencias de Prueba (Sessión 2)
| Input                                                                        | Output Esperado            | Output Obtenido         | Resultado |
| ---------------------------------------------------------------------------- | -------------------------- | ----------------------- | --------- |
| Me gusta Elden Ring y juego en Windows, ¿que me recomiendas?                 | JSON con output string     | Mock: Has preguntado... | Pase      |
| Soy de Mac y me encantan los juegos de estrategia, ¿cual deberia comprar?    | JSON con output string     | Mock: Has preguntado... | Pase      |
| (Vacio)                                                                      | JSON Error "INVALID_INPUT" | Error (INVALID_INPUT)   | Pase      |
