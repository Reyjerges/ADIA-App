import os
import gradio as gr
from groq import Groq

# 1. Configuración del Cliente
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: No configuraste la variable GROQ_API_KEY en Render."

    # Personalidad de Ingeniería Robótica (Modo Jarvis/Stark)
    system_prompt = (
        "Eres ADIA, el sistema operativo de ingeniería robótica de Jorge. "
        "Tu objetivo es asistir en cálculos cinemáticos, programación de microcontroladores y diseño mecánico. "
        "Eres técnica, eficiente y siempre llamas a Jorge por su nombre. "
        "Si Jorge te pide ayuda con un proyecto, ofreces soluciones prácticas con materiales disponibles."
    )
    
    # 2. Construcción de mensajes con limpieza de metadatos (Evita Error 400)
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    for interaccion in historial:
        # Extraemos solo el texto para que Groq no de error
        if isinstance(interaccion, dict):
            role = interaccion.get("role")
            content = interaccion.get("content")
            if role and content:
                mensajes_api.append({"role": role, "content": str(content)})
        else:
            # Soporte para formato de lista antiguo de Gradio
            u, b = interaccion
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    # Añadir el mensaje actual del usuario
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # 3. Llamada a la API de Groq
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=2048
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error en los propulsores (API): {str(e)}"

# --- INTERFAZ DE USUARIO ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA - Sistema de Ingeniería Robótica")
    gr.Markdown("Bienvenido, Jorge. Sistema listo para análisis técnico.")
    
    chat = gr.ChatInterface(
        fn=responder_adia,
        type="messages", # Optimizado para las versiones más nuevas de Gradio
        examples=["ADIA, calcula el torque de un motor", "Código para ESP32", "Estado del sistema"]
    )

if __name__ == "__main__":
    # Configuración obligatoria para Render
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(
        server_name="0.0.0.0",
        server_port=server_port,
        share=False
    )
