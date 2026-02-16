import os
import gradio as gr
from groq import Groq

# Configuración del Cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    # El "ADN" de tu JARVIS personal
    system_prompt = (
        "Eres ADIA, el sistema operativo de asistencia técnica de Jorge. "
        "Tu tono es profesional, eficiente y leal. "
        "Te diriges a tu creador como 'Señor' o 'Jorge'. "
        "Eres experto en ingeniería de bajo presupuesto y el proyecto 'Sentido Arácnido'. "
        "Tu misión es ayudar a Jorge a construir tecnología con lo que tenga a mano."
    )
    
    mensajes_para_api = [{"role": "system", "content": system_prompt}]
    
    # PROCESAMIENTO DE MEMORIA COMPATIBLE
    # En versiones antiguas de Gradio, el historial es una lista de listas [[usuario, bot], ...]
    for usuario_pasado, bot_pasado in historial:
        if usuario_pasado:
            mensajes_para_api.append({"role": "user", "content": str(usuario_pasado)})
        if bot_pasado:
            mensajes_para_api.append({"role": "assistant", "content": str(bot_pasado)})
    
    # Mensaje actual del usuario
    mensajes_para_api.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_para_api,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Señor, los servidores reportan una anomalía: {str(e)}"

# Interfaz de Gradio (Versión compatible sin el argumento 'type')
demo = gr.ChatInterface(
    fn=responder_adia,
    title="ADIA - Jarvis System",
    description="Protocolo de asistencia activa para el Proyecto Sentido Arácnido."
)

if __name__ == "__main__":
    # Solución al error de puertos de Render
    puerto = int(os.environ.get("PORT", 7860))
    
    demo.launch(
        server_name="0.0.0.0", 
        server_port=puerto,
        share=False
    )
