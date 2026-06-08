import gradio as gr
import requests
import json

BACKEND_URL = "http://localhost:8000/predict"

def predict_videojuego(user_input, platform):
    if not user_input or not user_input.strip():
        return "Por favor, introduce un juego válido.", "", {}

    payload = {
        "input": user_input.strip(),
        "platform": platform,
        "options": {
            "temperature": 0.2,
            "max_tokens": 600
        }
    }

    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=15)
        try:
            data = response.json()
        except ValueError:
            return (
                "Respuesta no válida",
                f"El servidor respondió con un formato no válido (Código HTTP {response.status_code}).\n\nPor favor, contacta con soporte o comprueba los registros del servidor backend.",
                {"response_text": response.text[:1000]}
            )

        if response.status_code == 200 and data.get("ok"):
            juego = data.get("output", "Sin respuesta.")
            motivo = data.get("motivo", "Sin motivo.")
            meta = data.get("meta", {})
            return juego, motivo, meta
        else:
            error = data.get("error", {}) if isinstance(data, dict) else {}
            msg = error.get("message", "Error inesperado en el servidor.")
            return (
                "Error del servidor",
                f"El servidor backend devolvió un error:\n\n{msg}",
                data if isinstance(data, dict) else {}
            )

    except requests.exceptions.Timeout as e:
        return (
            "Tiempo de espera agotado",
            "El servidor de recomendaciones tardó demasiado en responder.\n\nPor favor, verifica el estado del backend e inténtalo de nuevo.",
            {"error": "Timeout", "details": str(e)}
        )
    except requests.exceptions.ConnectionError as e:
        return (
            "Error de conexión",
            "No se pudo conectar con el servidor de recomendaciones.\n\nPor favor, asegúrate de que el servicio backend esté ejecutándose en http://localhost:8000.",
            {"error": "ConnectionError", "details": str(e)}
        )
    except Exception as e:
        return (
            "Error inesperado",
            f"Ocurrió un error inesperado al intentar comunicarse con el backend:\n\n{str(e)}",
            {"error": type(e).__name__, "details": str(e)}
        )

# Interfaz UI
with gr.Blocks(title="Ayudante de Videojuegos") as demo:
    gr.Markdown("# 🎮 Ayudante de Videojuegos")
    gr.Markdown("Recomendaciones profesionales basadas en tus gustos y plataforma.")

    with gr.Row():
        with gr.Column():
            platform_selector = gr.Radio(
                choices=["Windows", "Linux", "Mac"], 
                value="Windows", 
                label="Plataforma de juego"
            )
            input_text = gr.Textbox(
                label="¿A qué has estado jugando?", 
                placeholder="Ej: Counter Strike, Elden Ring, Skyrim...", 
                lines=3
            )
            btn = gr.Button("¡Dame una recomendación!", variant="primary")
        
        with gr.Column():
            output_game = gr.Textbox(label="🎮 Juego Recomendado", interactive=False)
            output_reason = gr.Textbox(label="💡 Motivo", interactive=False, lines=4)
            output_meta = gr.JSON(label="⚙️ Metadatos de la llamada")

    btn.click(
        fn=predict_videojuego, 
        inputs=[input_text, platform_selector], 
        outputs=[output_game, output_reason, output_meta]
    )
    


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
