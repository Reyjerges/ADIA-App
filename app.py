# ADIA - SISTEMA DE ASISTENCIA TÉCNICA
# Archivo: app.py
# Función: Interfaz de IA simplificada y estable para asistencia en ingeniería.

import os
import gradio as gr
from groq import Groq

# Configuración del Cliente
# La clave de API se obtiene de las variables de entorno
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    """
    Función de respuesta para el chat. 
    Procesa el mensaje del usuario y devuelve la respuesta de la IA.
    """
    if not api_key:
        return "Error: No se encontró la GROQ_API_KEY en las variables de entorno."

    # Definición de personalidad: IA profesional y técnica
    system_prompt = (
        "Eres ADIA, una inteligencia artificial especializada en asistencia técnica. "
        "Tu objetivo es ayudar a Jorge con sus proyectos de ingeniería, robótica y ciencia. "
        "Eres útil, directa, educada y proporcionas explicaciones claras y precisas. "
        "Te centras en datos técnicos, seguridad y apoyo educativo real."
    )
    
    # Construcción de la lista de mensajes para la API de Groq
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # Manejo del historial: Gradio suele pasar el historial como una lista de listas [[user, bot], ...]
    if historial:
        for interaccion in historial:
            # Verificamos que la interacción sea un formato válido
            if isinstance(interaccion, (list, tuple)) and len(interaccion) == 2:
                u, b = interaccion
                if u: mensajes_api.append({"role": "user", "content": str(u)})
                if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    # Añadir mensaje actual del usuario
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Llamada a la API de Groq usando el modelo Llama 3
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Lo siento, ocurrió un error al procesar tu solicitud: {str(e)}"

# --- INTERFAZ DE USUARIO ---
# Utilizamos la configuración más básica para garantizar compatibilidad total
with gr.Blocks(title="ADIA v3.7") as demo:
    gr.Markdown("# ADIA - Asistente de Ingeniería")
    gr.Markdown("Interfaz de soporte técnico para proyectos y desarrollo científico.")
    
    # ChatInterface sin argumentos adicionales para evitar errores de versión
    chat = gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    # Configuración de puerto para ejecución local o en servidor (Render/HuggingFace)
    server_port = int(os.environ.get("PORT", 7860))
    
    print(f"Iniciando ADIA en el puerto {server_port}...")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=server_port,
        quiet=True
    )
