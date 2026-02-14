import gradio as gr
from groq import Groq
import os

# Configuración del motor de inteligencia
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_core(mensaje, historial):
    # Sistema básico para ADIA
    sistema = {
        "role": "system",
        "content": "Eres ADIA v1.2. Experta en IA y programación de ML. Responde técnico pero fácil de entender."
    }

    mensajes_validados = [sistema]

    # Validamos historial de forma segura
    if historial:
        for item in historial:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                usuario, bot = item
                if usuario:
                    mensajes_validados.append({"role": "user", "content": str(usuario)})
                if bot:
                    mensajes_validados.append({"role": "assistant", "content": str(bot)})

    # Añadimos el mensaje actual solo si no está vacío
    if mensaje:
        mensajes_validados.append({"role": "user", "content": str(mensaje)})

    try:
        busqueda = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_validados,
            temperature=0.4
        )
        contenido = busqueda.choices[0].message["content"]
        return contenido
    except Exception as e:
        return f"⚠️ ERROR DE SISTEMA: {str(e)}"

# --- INTERFAZ minimalista ---
with gr.Blocks() as app:
    chatbot = gr.Chatbot(label="ADIA", height=450)
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Escribe algo para ADIA...",
            scale=4
        )
        btn = gr.Button("ENVIAR", variant="primary", scale=1)

    limpiar = gr.Button("Reiniciar Memoria")

    # Función de respuesta
    def responder(m, h):
        if not m:
            return "", h
        respues
