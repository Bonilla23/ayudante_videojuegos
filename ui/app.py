import gradio as gr
import requests
import json

BACKEND_URL = "http://localhost:8000/predict"

def predict_videojuego(user_input, platform):
    if not user_input or not user_input.strip():
        return "Por favor, introduce una pregunta válida.", "", {}

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
        data = response.json()

        if response.status_code == 200 and data.get("ok"):
            juego = data.get("output", "Sin respuesta.")
            motivo = data.get("motivo", "Sin motivo.")
            meta = data.get("meta", {})
            return juego, motivo, meta
        else:
            error = data.get("error", {})
            msg = error.get("message", "Error inesperado")
            return f"Error: {msg}", "", data

    except Exception as e:
        return f"Error de conexión: {str(e)}", "", {}

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
