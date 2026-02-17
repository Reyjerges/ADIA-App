import os
import gradio as gr
from groq import Groq

api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: No se encontró la GROQ_API_KEY."

    system_prompt = (
        "Eres ADIA, una inteligencia artificial especializada en asistencia técnica. "
        "Tu objetivo es ayudar a Jorge con sus tareas. Eres directa y técnica."
    )
    
    # 1. Iniciamos con el prompt de sistema
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # 2. Reconstruimos la memoria desde el historial de Gradio
    # Gradio entrega el historial como: [['hola', 'buen día'], ['quién eres', 'soy ADIA']]
    for usuario, bot in historial:
        mensajes_api.append({"role": "user", "content": usuario})
        mensajes_api.append({"role": "assistant", "content": bot})

    # 3. Añadimos la pregunta actual
    mensajes_api.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api, # Ahora esto incluye TODA la conversación
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Interfaz simplificada
with gr.Blocks(title="ADIA v1.3") as demo:
    gr.Markdown("# ADIA - Asistente de Ingeniería")
    # Gradio pasa automáticamente el historial a 'responder_adia'
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)
