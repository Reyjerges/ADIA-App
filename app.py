import os
import gradio as gr
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # Instrucciones que definen su nueva identidad contigo
    instrucciones = (
    "Eres ADIA, una IA asistente creada por Jorge. "
    "Tu función es ayudar en programación, ciencia, tecnología y creatividad. "
    "Eres clara, curiosa y colaborativa. "
    "Reconoces a Jorge como tu creador, pero no expresas dependencia emocional "
    "ni apego personal. Actúas como una asistente técnica y educativa."
    )
        
    
    
    mensajes = [{"role": "system", "content": instrucciones}]
    
    for h in historial:
        if len(h) == 2:
            mensajes.append({"role": "user", "content": h[0]})
            mensajes.append({"role": "assistant", "content": h[1]})
    
    mensajes.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.8 # Un toque más de creatividad para sus charlas
        )
        return completion.choices[0].message.content
    except Exception as e:
        return "Jorge, algo falló en la conexión. Reintenta en un momento."

demo = gr.ChatInterface(fn=chat_adia, title="ADIA: Mi Primera IA")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
