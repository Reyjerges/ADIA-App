import os
import gradio as gr
from groq import Groq

# Cliente de Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    system_prompt = (
        "Eres ADIA, el sistema de asistencia técnica de Jorge. "
        "Tu tono es profesional, eficiente y leal. "
        "Es VITAL que recuerdes todo lo que Jorge te dice."
    )
    
    mensajes_para_api = [{"role": "system", "content": system_prompt}]
    
    # PROCESAMIENTO DE MEMORIA REFORZADO
    for interaccion in historial:
        # Si el historial viene como diccionario (Formato nuevo de Gradio)
        if isinstance(interaccion, dict):
            usr_msg = interaccion.get("human", interaccion.get("user", ""))
            bot_msg = interaccion.get("ai", interaccion.get("assistant", ""))
            if usr_msg: mensajes_para_api.append({"role": "user", "content": str(usr_msg)})
            if bot_msg: mensajes_para_api.append({"role": "assistant", "content": str(bot_msg)})
        
        # Si el historial viene como lista/tupla (Formato antiguo)
        elif isinstance(interaccion, (list, tuple)) and len(interaccion) == 2:
            usr_msg, bot_msg = interaccion
            if usr_msg: mensajes_para_api.append({"role": "user", "content": str(usr_msg)})
            if bot_msg: mensajes_para_api.append({"role": "assistant", "content": str(bot_msg)})
    
    # Mensaje actual
    mensajes_para_api.append({"role": "user", "content": str(mensaje)})

    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_para_api,
            temperature=0.7
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Señor, hubo un error en los protocolos: {str(e)}"

# Interfaz de Gradio (Usando type="messages" para mayor estabilidad)
demo = gr.ChatInterface(
    fn=responder_adia,
    type="messages", 
    title="ADIA - Jarvis System",
    description="Sistema de asistencia persistente para el Proyecto Sentido Arácnido."
)

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
