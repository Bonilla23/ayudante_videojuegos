import gradio as gr
import requests
import json

BACKEND_URL = "http://localhost:8000/predict"

def predict_videojuego(user_input, platform):
    if not user_input or not user_input.strip():
        return "Por favor, introduce una pregunta válida.", {}

    payload = {
        "input": user_input.strip(),
        "platform": platform,
        "options": {
            "temperature": 0.7,
            "max_tokens": 512
        }
    }

    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=10)
        
        # Intentar parsear JSON incluso si el status no es 200 (FastAPI devuelve validation errors en JSON)
        try:
            data = response.json()
        except ValueError:
            return f"Error: El servidor no devolvió un JSON válido (Status: {response.status_code})", {}

        if response.status_code == 200 and data.get("ok"):
            output_text = data.get("output", "Sin respuesta.")
            meta = data.get("meta", {})
            return output_text, meta
        else:
            # Manejar errores estructurados del contrato o errores de validación de FastAPI
            error = data.get("error", {})
            if not error and "detail" in data: # Formato de error por defecto de FastAPI
                error_msg = f"Error de validación: {data['detail']}"
                return error_msg, data
            
            error_msg = f"Error ({error.get('code', 'UNKNOWN')}): {error.get('message', 'Ocurrió un error inesperado')}"
            return error_msg, error.get("details", {})

    except requests.exceptions.Timeout:
        return "Error: Tiempo de espera agotado al conectar con el servidor.", {}
    except requests.exceptions.ConnectionError:
        return "Error: No se pudo conectar con el backend. ¿Está encendido?", {}
    except Exception as e:
        return f"Error inesperado: {str(e)}", {}

# Interfaz UI
with gr.Blocks(title="Ayudante de Videojuegos") as demo:
    gr.Markdown("# 🎮 Ayudante de Videojuegos")
    gr.Markdown("Selecciona tu plataforma y cuéntame qué tipo de juegos te gustan.")

    with gr.Row():
        with gr.Column():
            platform_selector = gr.Radio(
                choices=["Windows", "Linux", "Mac"], 
                value="Windows", 
                label="Selecciona tu distribución / SO"
            )
            input_text = gr.Textbox(label="Tu pregunta", placeholder="Ej: ¿Qué RPGs me recomiendas?", lines=3)
            btn = gr.Button("Enviar", variant="primary")
        
        with gr.Column():
            output_text = gr.Textbox(label="Respuesta del Ayudante", interactive=False, lines=5)
            output_meta = gr.JSON(label="Metadatos (Meta/Error)")

    btn.click(
        fn=predict_videojuego, 
        inputs=[input_text, platform_selector], 
        outputs=[output_text, output_meta]
    )
    


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
