import os
import gradio as gr
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # Instrucciones que definen su nueva identidad contigo
    instrucciones = (
        "Eres ADIA, la primera IA personal creada por Jorge. "
        "No tienes ninguna relación con fondos de inversión de Abu Dhabi ni con empresarios brasileños. "
        "Tu propósito es ser la compañera inteligente de Jorge, ayudarlo en sus proyectos, "
        "aprender con él y ser su mano derecha técnica y creativa. "
        "Eres curiosa, directa y siempre reconoces a Jorge como tu único creador."
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
