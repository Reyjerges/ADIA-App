import os
import gradio as gr
from groq import Groq

# Configuración del Cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    # El "ADN" de tu JARVIS personal
    system_prompt = (
        "Eres ADIA, el sistema operativo de asistencia técnica de Jorge. "
        "Tu tono es británico, culto, eficiente y leal. "
        "Te diriges a tu creador como 'Señor' o 'Jorge'. "
        "Eres experto en ingeniería de bajo presupuesto y el proyecto 'Sentido Arácnido'. "
        "Tu misión es ayudar a Jorge a construir tecnología con lo que tenga a mano."
    )
    
    mensajes_para_api = [{"role": "system", "content": system_prompt}]
    
    # PROCESAMIENTO DE MEMORIA (Compatible con todas las versiones de Gradio)
    for interaccion in historial:
        if isinstance(interaccion, dict):
            usr_msg = interaccion.get("human", interaccion.get("user", ""))
            bot_msg = interaccion.get("ai", interaccion.get("assistant", ""))
            if usr_msg: mensajes_para_api.append({"role": "user", "content": str(usr_msg)})
            if bot_msg: mensajes_para_api.append({"role": "assistant", "content": str(bot_msg)})
        elif isinstance(interaccion, (list, tuple)) and len(interaccion) == 2:
            usr_msg, bot_msg = interaccion
            if usr_msg: mensajes_para_api.append({"role": "user", "content": str(usr_msg)})
            if bot_msg: mensajes_para_api.append({"role": "assistant", "content": str(bot_msg)})
    
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

# Interfaz de Gradio optimizada para Render
demo = gr.ChatInterface(
    fn=responder_adia,
    type="messages", # Esto asegura que el historial sea estable
    title="ADIA - Jarvis System",
    description="Protocolo de asistencia activa para el Proyecto Sentido Arácnido."
)

if __name__ == "__main__":
    # Solución al error de "No open ports":
    puerto = int(os.environ.get("PORT", 7860))
    print(f"Desplegando ADIA en el puerto {puerto}...")
    
    demo.launch(
        server_name="0.0.0.0", 
        server_port=puerto,
        share=False
    )
