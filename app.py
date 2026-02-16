import os
import gradio as gr
from groq import Groq

# Cliente de Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    # 1. Definimos su personalidad de JARVIS
    system_prompt = (
        "Eres ADIA, el sistema de asistencia técnica de Jorge. "
        "Tu tono es profesional, eficiente y leal. "
        "Es VITAL que recuerdes todo lo que Jorge te dice en esta sesión."
    )
    
    # 2. Creamos la lista de mensajes empezando por el sistema
    mensajes_para_api = [{"role": "system", "content": system_prompt}]
    
    # 3. AGREGAMOS EL HISTORIAL (Esto es lo que activa la memoria)
    for interaccion in historial:
        # Gradio guarda el historial como [usuario, bot]
        usuario_pasado = interaccion[0]
        bot_pasado = interaccion[1]
        
        if usuario_pasado:
            mensajes_para_api.append({"role": "user", "content": str(usuario_pasado)})
        if bot_pasado:
            mensajes_para_api.append({"role": "assistant", "content": str(bot_pasado)})
    
    # 4. Agregamos el mensaje que Jorge acaba de escribir
    mensajes_para_api.append({"role": "user", "content": str(mensaje)})

    try:
        # 5. Enviamos TODO el paquete a la API
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_para_api,
            temperature=0.7
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error en los servidores, Señor: {str(e)}"

# Interfaz de Gradio
demo = gr.ChatInterface(
    fn=responder_adia,
    title="ADIA - Jarvis System",
    description="Protocolo de asistencia para el Proyecto Sentido Arácnido."
)

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
