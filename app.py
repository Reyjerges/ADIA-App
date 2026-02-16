import os
import gradio as gr
from groq import Groq

# Configuración del Cliente - Asegúrate de tener la API KEY en las variables de entorno de Render
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    # 1. Definimos la identidad de ADIA
    system_prompt = "Eres ADIA, una IA experta en física y robótica. Tu objetivo es ayudar y ser una compañera para que el usuario se sienta comodo hablando contigo y que pueda aprender de lo que te pregunta."
    
    # 2. Iniciamos la lista de mensajes con el sistema
    mensajes_redactados = [{"role": "system", "content": system_prompt}]
    
    # 3. Construimos la memoria: añadimos los mensajes anteriores
    # Gradio pasa el historial como una lista de listas: [[usuario, bot], [usuario, bot]...]
    for chat in historial:
        if len(chat) == 2:
            usr, bot = chat
            if usr:
                mensajes_redactados.append({"role": "user", "content": str(usr)})
            if bot:
                mensajes_redactados.append({"role": "assistant", "content": str(bot)})
    
    # 4. Añadimos el mensaje actual del usuario
    mensajes_redactados.append({"role": "user", "content": str(mensaje)})

    try:
        # 5. Llamada a la API de Groq
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_redactados,
            temperature=0.7,
            max_tokens=2048
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error en la API: {e}")
        return "ADIA: Lo siento, Jorge. Hubo un parpadeo en mi memoria. ¿Podrías repetir eso?"

# 6. Interfaz de Gradio (ChatInterface ya maneja el historial automáticamente)
demo = gr.ChatInterface(
    fn=responder_adia, 
    title="ADIA - Expert Robotics AI",
    description="Interfaz avanzada para el desarrollo de sistemas de asistencia motriz."
)

if __name__ == "__main__":
    # Render usa la variable de entorno PORT
    puerto = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
