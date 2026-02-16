import os
import gradio as gr
from groq import Groq

# Configuración del cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    instrucciones = "Eres ADIA, una IA experta en física y robótica."
    mensajes = [{"role": "system", "content": instrucciones}]
    
    for usuario, asistente in historial:
        mensajes.append({"role": "user", "content": usuario})
        mensajes.append({"role": "assistant", "content": asistente})
    
    mensajes.append({"role": "user", "content": mensaje})

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=mensajes,
        temperature=0.7
    )
    return completion.choices[0].message.content

# Quitamos 'theme' por ahora para evitar el TypeError
# Si quieres diseño, Gradio lo pone automático en su versión moderna
demo = gr.ChatInterface(
    fn=responder_adia,
    title="ADIA IA"
)

if __name__ == "__main__":
    # Obtenemos el puerto de Render
    puerto = int(os.environ.get("PORT", 7860))
    # Lanzamos la app
    demo.launch(server_name="0.0.0.0", server_port=puerto)
  
