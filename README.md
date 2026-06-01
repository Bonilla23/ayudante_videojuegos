# Ayudante de Videojuegos (Recomendador Inteligente)

Este proyecto es un asistente inteligente que recomienda videojuegos basados en tus gustos y tu plataforma de escritorio, utilizando LLMs de **Azure AI Foundry (DeepSeek-V4-Flash)** y una arquitectura de pre-filtrado local (**RAG**) para ofrecer sugerencias personalizadas de forma rápida, económica y altamente robusta.

---

## Despliegue y Ejecución Rápida

### 1. Requisitos Previos e Instalación
Clona el repositorio e instala las dependencias necesarias en tu entorno virtual:
```bash
# Crear entorno virtual (si no lo tienes)
python -m venv .venv
.venv\Scripts\activate  # En Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno (`.env`)
Crea un archivo `.env` en la raíz del proyecto con la siguiente configuración:
```env
GROUP_ID="G1"
LOG_PATH="logs/logs.jsonl"

# Configuración de Azure AI Foundry (DeepSeek)
AZURE_OPENAI_ENDPOINT="https://your-resource.services.ai.azure.com"
AZURE_OPENAI_BASE_URL="https://your-resource.services.ai.azure.com/model/version"
AZURE_OPENAI_DEPLOYMENT_NAME="DeepSeek-V4-Flash"
AZURE_OPENAI_API_KEY="TU_API_KEY_AQUI"
```

### 3. Lanzar el Servidor Backend (FastAPI)
Puedes ejecutar el servidor en dos modalidades independientes:
*   **Modo Real (Azure Foundry - Recomendado):**
    ```bash
    .venv\Scripts\python.exe backend/server_foundry.py
    ```
*   **Modo Mock (Plan B de Contingencia Local):**
    ```bash
    .venv\Scripts\python.exe backend/server_mock.py
    ```
    *Nota: El modo mock imita el 100% de la lógica del contrato pero responde de forma local en 10ms a coste cero.*

### 4. Lanzar la Interfaz de Usuario (Gradio UI)
Con el backend corriendo en otra terminal, levanta la interfaz gráfica:
```bash
.venv\Scripts\python.exe ui/app.py
```
Accede a la interfaz en tu navegador en: **`http://127.0.0.1:7860`**

---

## Estructura del Repositorio

*   `backend/server_foundry.py`: API FastAPI principal con conexión real a Azure AI Foundry y lógica RAG local.
*   `backend/server_mock.py`: API FastAPI alternativa con respuestas locales simuladas (Plan B de contingencia).
*   `ui/app.py`: Interfaz de usuario interactiva y responsiva desarrollada en Gradio.
*   `data/steam_clean.json`: Base de datos local optimizada de Steam (8,762 juegos) usada para el RAG.
*   `logs/logs.jsonl`: Archivo de telemetría estructurado que registra el consumo y la latencia en vivo.
*   `tests/`: Carpeta que contiene las suites de pruebas de calidad:
    *   `run_eval.py`: Evaluación automatizada original (10 casos de prueba).
    *   `run_eval_extended.py`: Nueva suite de pruebas optimizada con **25 casos de prueba** (objetivo final).
    *   `calculate_percentiles.py`: Script de telemetría para calcular los percentiles de latencia **p50 y p95** en tiempo real.

---

## Pruebas y Calidad de Software

### Ejecutar Suite de Calidad de 10 casos
```bash
.venv\Scripts\python.exe tests/run_eval.py
```
*Guarda resultados en `tests/eval_report.json`.*

### Ejecutar Suite Extendida de 25 casos (Objetivo Final)
```bash
.venv\Scripts\python.exe tests/run_eval_extended.py
```
*Guarda resultados estructurados en `tests/eval_report_extended.json`.*

### Calcular Métricas de Operabilidad (Percentiles de Latencia)
Puedes analizar en tiempo real la telemetría de tus logs de producción ejecutando:
```bash
.venv\Scripts\python.exe tests/calculate_percentiles.py
```
*Imprime la latencia mínima, máxima, mediana (p50) y peor caso común (p95) basados en tu consumo real.*

---

## Mitigaciones de Fiabilidad Implementadas

El sistema está diseñado bajo estrictas políticas de resiliencia ante fallos externos de red o del proveedor cloud:
1.  **Validación en frontera (Pydantic):** Rechazo inmediato de solicitudes vacías o plataformas no soportadas antes de llamar al LLM (HTTP 400).
2.  **Timeouts robustos:** Timeout de 15 segundos en las llamadas cliente-servidor para evitar bloqueos del navegador.
3.  **Backoff exponencial:** Reintentos automáticos integrados a nivel de SDK ante errores de saturación (429) y caídas de Azure (5xx).
4.  **Respuestas consistentes:** Captura de excepciones en backend para responder siempre con JSON estructurado en lugar de stacktraces expuestos.
