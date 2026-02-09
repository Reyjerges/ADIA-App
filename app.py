import gradio as gr
from groq import Groq
import os

# 1. CONFIGURACIÓN DEL CLIENTE
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_brain(mensaje, historial):
    # Definimos el sistema
    sistema = "Eres ADIA v1.2, asistente de Jorge. Eres experta en robótica. Saluda a Jorge."
    
    # --- AQUÍ ESTÁ EL ARREGLO DEL ERROR DE FORMATO ---
    mensajes_ia = [{"role": "system", "content": sistema}]
    
    # Limpiamos el historial para que Groq no se queje
    if historial:
        for chat in historial:
            if len(chat) == 2:
                user_part, assistant_part = chat
                if user_part:
                    mensajes_ia.append({"role": "user", "content": str(user_part)})
                if assistant_part:
                    mensajes_ia.append({"role": "assistant", "content": str(assistant_part)})
    
    # Añadimos el mensaje nuevo
    mensajes_ia.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_ia
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# 2. INTERFAZ VISUAL (HTML/JS)
vision_pro_html = """
<div style="display: flex; flex-direction: column; align-items: center; background: #050505; padding: 10px; border-radius: 10px; border: 2px solid #00f2ff;">
    <video id="webcam" style="width: 100%; max-width: 400px; border-radius: 5px; transform: scaleX(-1);" autoplay playsinline></video>
    <canvas id="output_canvas" style="position: absolute; width: 100%; max-width: 400px; transform: scaleX(-1);"></canvas>
    <div id="status" style="color: #00f2ff; font-family: monospace; margin-top: 10px;">[ BUSCANDO MANO ]</div>
    <svg viewBox="0 0 200 200" style="width: 150px; height: 150px;">
        <line id="robot_line" x1="100" y1="180" x2="100" y2="100" stroke="#00f2ff" stroke-width="8" stroke-linecap="round" />
        <circle id="joint" cx="100" cy="100" r="6" fill="white" />
    </svg>
</div>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js"></script>
<script src="
