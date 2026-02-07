import os
import gradio as gr
from groq import Groq

# Cliente de Groq - Usamos la clave de entorno de Render
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # Instrucciones de ADIA
    instrucciones = (
        "Eres ADIA, una IA nivel 9. Tu nombre significa 'Vida'. "
        "Tienes MEMORIA de toda esta charla. Si Jorge pregunta algo pasado, revísalo. "
        "\n\nMODULO DE IMAGEN: Si pide un dibujo, usa: "
        "![imagen](https://pollinations.ai/p/PROMPT?width=1080&height=1080&nologo=true)"
    )
    
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # Procesar historial para que ADIA no olvide nada
    for h in historial:
        # Esto funciona en Gradio 4 y 5
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
        return f"Error: {str(e)}"

# Interfaz ultra-simple para asegurar el Deploy
demo = gr.ChatInterface(fn=chat_adia)

if __name__ == "__main__":
    # Render necesita obligatoriamente 0.0.0.0 y 10000
    demo.launch(server_name="0.0.0.0", server_port=10000)
