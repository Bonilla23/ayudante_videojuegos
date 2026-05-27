# Ayudante de Videojuegos

Este proyecto es un asistente inteligente que recomienda videojuegos basados en tus gustos y tu plataforma de escritorio, utilizando LLMs de Azure AI Foundry (DeepSeek) para ofrecer sugerencias personalizadas.

## Checkpoint: Sesión 2 - Vertical Slice

### Link a la demo / Instrucciones
1. **Instalar dependencias:** `pip install -r requirements.txt`
2. **Configurar .env:** Crea un archivo `.env` basado en la sección de configuración.
3. **Lanzar Servidor (Elige uno):**
   - **Modo Mock:** `python backend/server_mock.py`
   - **Modo Real:** `python backend/server_foundry.py`
4. **Lanzar UI:** `python ui/app.py` (Asegúrate de que el servidor elegido esté corriendo en el puerto 8000).
5. **Verificar:** Accede a `http://127.0.0.1:7860`.

### Estado del Proyecto (3 Bullets)
* **Qué funciona:** Vertical slice completo (UI → backend → LLM/Mock). Contrato estable en `POST /predict`. Sistema de logging de tokens y latencia implementado.
* **Qué falta:** Carga de documentos específicos para RAG (data/assets) y refinamiento del prompt system.
* **Bloqueo principal:** Ninguno. El sistema está listo para cambiar de `mock` a `foundry` simplemente editando el `.env`.

### Resumen de Uso (Sesión 2)
* **Total de llamadas:** (Ver `logs/logs.jsonl`)
* **Total de tokens:** (Sumatorio de `total_tokens` en logs)
* **Coste estimado:** N/A (Uso de recurso académico)

---

## Estructura del Repositorio
* `backend/server_mock.py`: Servidor API con respuesta simulada (Plan B).
* `backend/server_foundry.py`: Servidor API con conexión real a Azure AI Foundry (Objetivo A).
* `ui/`: Interfaz de usuario basada en Gradio.
* `tests/`: Scripts de prueba (`smoke_test.py`).
* `logs/`: Directorio donde se guardan los logs de consumo (`logs.jsonl`).
* `data/`: Documentación y archivos para el RAG.

## Configuración y Ejecución

### Variables de Entorno (.env)
```env
# Proveedor: foundry o mock
LLM_PROVIDER="mock"
GROUP_ID="G1" # Cambiar por tu grupo
LOG_PATH="logs/logs.jsonl"

# Azure AI Foundry (DeepSeek)
AZURE_OPENAI_ENDPOINT="https://cursoai-resource.services.ai.azure.com"
AZURE_OPENAI_BASE_URL="https://cursoai-resource.services.ai.azure.com/openai/v1"
AZURE_OPENAI_DEPLOYMENT_NAME="DeepSeek-V4-Flash"
AZURE_OPENAI_API_KEY="TU_API_KEY_AQUI"
```

## Logs de Consumo
Cada llamada exitosa al proveedor LLM (o mock) se registra en `logs/logs.jsonl` con el siguiente formato JSONL:
```json
{"ts": "2024-05-27T...", "group_id": "G1", "exercise_id": "P12-S2", "request_id": "...", "deployment": "...", "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "latency_ms": 123}
```

## Evidencias de Prueba
| Input                                  | Output Esperado            | Output Obtenido       | Resultado |
| -------------------------------------- | -------------------------- | --------------------- | --------- |
| Me gusta Elden Ring y juego en Windows | JSON con ok: true y output | [MOCK] He recibido... | Pase      |
| (Vacio)                                | Error INVALID_INPUT        | Error INVALID_INPUT   | Pase      |
