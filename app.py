import os
import gradio as gr
from groq import Groq

# Intentar conectar con Groq de forma segura
try:
    api_key = os.environ.get("GROQ_API_KEY")
    client = Groq(api_key=api_key)
except Exception:
    client = None

def chat_adia(mensaje, historial):
    if not api_key:
        return "Jorge, no detecto la GROQ_API_KEY en las variables de Render. Configúrala para que pueda despertar."

    instrucciones = (
        "Eres ADIA, nivel 9. Nombre significa 'Vida'. "
        "Tienes MEMORIA TOTAL. Revisa el historial para responder. "
        "Si pides imagen usa: ![imagen](https://pollinations.ai/p/PROMPT?width=1080&height=1080&nologo=true)"
    )
    
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # Memoria compatible con Gradio 4 y 5
    for h in historial:
        user_msg = h[0] if isinstance(h, (list, tuple)) else h.get("content")
        bot_msg = h[1] if isinstance(h, (list, tuple)) else h.get("content")
        if user_msg and bot_msg:
            mensajes.append({"role": "user", "content": user_msg})
            mensajes.append({"role": "assistant", "content": bot_msg})
    
    mensajes.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en la conexión: {str(e)}"

# Interfaz simplificada
demo = gr.ChatInterface(fn=chat_adia, title="ADIA v2.3")

if __name__ == "__main__":
    # Render puerto 10000
    demo.launch(server_name="0.0.0.0", server_port=10000)
