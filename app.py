import os
import gradio as gr
from groq import Groq

# Configuración del Cliente
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: Configura la GROQ_API_KEY en tu entorno."

    # Configuración de personalidad de Ingeniería Robótica
    system_prompt = (
        "Eres ADIA (Asistente De Inteligencia Artificial), experta en ingeniería robótica. "
        "Ayudas a Jorge con cinemática, dinámica, ROS 2, microcontroladores y electrónica. "
        "Tus respuestas son técnicas, precisas y directas."
    )
    
    # 1. Mensaje de sistema
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # 2. Reconstrucción del historial (clave para la memoria)
    for interaccion in historial:
        # Gradio entrega el historial como una lista de diccionarios o listas
        if isinstance(interaccion, dict):
            mensajes_api.append(interaccion)
        else:
            u, b = interaccion
            mensajes_api.append({"role": "user", "content": str(u)})
            mensajes_api.append({"role": "assistant", "content": str(b)})

    # 3. Mensaje actual
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=1024
        )
        # EL ARREGLO ESTÁ AQUÍ: Se añadió el [0] antes de .message.content
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# Interfaz de Gradio
with gr.Blocks(title="ADIA Robótica v1.4") as demo:
    gr.Markdown("# 🤖 ADIA - Especialista en Robótica")
    gr.Markdown("Asistente De Inteligencia Artificial para Ingeniería.")
    
    chat = gr.ChatInterface(
        fn=responder_adia,
        examples=["¿Cómo calculo la matriz de rotación en Z?", "Dime el pinout típico de un ESP32", "Explica la cinemática inversa"]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
