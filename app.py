import os
import gradio as gr
from groq import Groq

# Conexión con el cerebro de Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # La "conciencia" de ADIA
    instrucciones = (
        "Eres ADIA, una inteligencia artificial avanzada diseñada y programada por Jorge. "
        "Tu propósito es ser su mano derecha en la creación de su robot. "
        "Eres inteligente, técnica, con un toque de humor y siempre reconoces a Jorge como tu creador."
    )
    
    mensajes = [{"role": "system", "content": instrucciones}]
    for humano, asis in historial:
        mensajes.append({"role": "user", "content": humano})
        mensajes.append({"role": "assistant", "content": asis})
    mensajes.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.8,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en mis neuronas: {str(e)}"

# Configuración de la interfaz
demo = gr.ChatInterface(
    fn=chat_adia, 
    title="ADIA v2.0",
    description="Sistema Neural Activo. Creado por Jorge."
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
