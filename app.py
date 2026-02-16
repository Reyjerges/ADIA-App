import os
import gradio as gr
from groq import Groq

# Cliente de Groq optimizado
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    # Personalidad de ADIA
    system_prompt = (
        "Eres ADIA, el sistema operativo de asistencia técnica de Jorge. "
        "Tu tono es profesional, eficiente y leal. "
        "Te diriges a tu creador como 'Señor' o 'Jorge'. "
        "Eres experto en ingeniería creativa y tecnología de bajo costo. "
        "Tu misión es ayudar a Jorge con el proyecto 'Sentido Arácnido'."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # Procesamiento de historial simplificado para mayor velocidad
    if historial:
        for usr, bot in historial:
            if usr: mensajes_api.append({"role": "user", "content": str(usr)})
            if bot: mensajes_api.append({"role": "assistant", "content": str(bot)})
    
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Usamos Llama 3.1 8B por ser el modelo más rápido y eficiente
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Señor, hay un retraso en la respuesta: {str(e)}"

# Interfaz minimalista para carga ultra-rápida
demo = gr.ChatInterface(
    fn=responder_adia,
    title="ADIA Core v1.6",
    description="Sistema de Asistencia Activa - Jorge"
)

if __name__ == "__main__":
    # Configuración de red para Render
    port = int(os.environ.get("PORT", 7860))
    demo.launch(
        server_name="0.0.0.0", 
        server_port=port,
        quiet=True # Reduce logs para agilizar el arranque
    )
