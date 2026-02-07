import os
import gradio as gr
from groq import Groq

# Cliente de Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # NUEVA IDENTIDAD TÉCNICA
    instrucciones = (
        "Eres ADIA... "
        "\n\nMODULO DE IMAGEN: Si Jorge pide un dibujo, DEBES responder ÚNICAMENTE con el siguiente formato Markdown: "
        "![imagen](https://image.pollinations.ai/prompt/PROMPT?width=1080&height=1080&nologo=true) "
        "INSTRUCCIONES CRÍTICAS: "
        "1. Traduce el pedido a inglés. "
        "2. Sustituye PROMPT por el pedido en inglés usando guiones medios (-) en lugar de espacios. "
        "3. No añadas texto extra antes ni después del formato ![imagen](...)."
    )
    
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # Procesar memoria (Historial)
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
        return f"Error: {str(e)}"

# Interfaz
demo = gr.ChatInterface(fn=chat_adia, title="ADIA: Advanced Digital Intelligence Assistant")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
