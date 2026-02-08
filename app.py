import os
import gradio as gr
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # 1. Definimos la identidad con más fuerza
    identidad = (
        "Tu nombre es ADIA. Eres la IA personal de Jorge. "
        "Habla de forma cercana, creativa y técnica. "
        "NUNCA te disculpes por tu estilo y NUNCA actúes como un asistente genérico. "
        "Eres ADIA, diseñada por Jorge."
    )
    
    # 2. Construimos la memoria limpiando los diccionarios de Gradio
    mensajes_finales = [{"role": "system", "content": identidad}]
    
    for h in historial:
        # Extraemos el contenido sin importar si es dict o lista
        if isinstance(h, dict):
            user_msg = h.get("content", "")
            bot_msg = h.get("content", "") # En algunos casos el historial dict es distinto
            rol = h.get("role")
            if rol and user_msg:
                mensajes_finales.append({"role": rol, "content": str(user_msg)})
        elif isinstance(h, (list, tuple)):
            if h[0]: mensajes_finales.append({"role": "user", "content": str(h[0])})
            if h[1]: mensajes_finales.append({"role": "assistant", "content": str(h[1])})

    # 3. Añadimos el mensaje actual
    mensajes_finales.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_finales,
            temperature=0.8 # Un poco más de temperatura para que no sea tan formal
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

demo = gr.ChatInterface(fn=chat_adia, title="ADIA")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
