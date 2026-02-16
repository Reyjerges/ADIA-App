import os
import gradio as gr
from groq import Groq

# Configuración del cliente de Groq
# Recuerda poner GROQ_API_KEY en las variables de entorno de Render
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    instrucciones = "Eres ADIA, una IA experta en física y robótica creada por un ingeniero de 7mo grado."
    
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # Añadimos el historial para que tenga memoria
    for usuario, asistente in historial:
        mensajes.append({"role": "user", "content": usuario})
        mensajes.append({"role": "assistant", "content": asistente})
    
    mensajes.append({"role": "user", "content": mensaje})

    # Petición a la API de Groq
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=mensajes,
        temperature=0.7
    )
    
    return completion.choices[0].message.content

# Interfaz de Gradio
demo = gr.ChatInterface(
    fn=responder_adia,
    title="ADIA IA",
    theme="soft"
)

if __name__ == "__main__":
    # Configuración crucial para Render:
    # Leemos el puerto que nos da Render o usamos el 7860 por defecto
    puerto = int(os.environ.get("PORT", 7860))
    
    # server_name "0.0.0.0" permite que la web sea accesible desde fuera
    demo.launch(server_name="0.0.0.0", server_port=puerto)
