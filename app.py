import os
import gradio as gr
from groq import Groq

# 1. Configuración del Cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # Instrucciones para la identidad y las imágenes
    instrucciones = (
        "Eres ADIA, la IA de Jorge. Revisa el historial para ser coherente. "
        "Si Jorge pide una imagen, usa EXACTAMENTE este formato: "
        "![imagen](https://image.pollinations.ai/prompt/PROMPT?nologo=true) "
        "Traduce el pedido a inglés y usa guiones en el PROMPT."
    )
    
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # 2. Procesamiento del historial (Compatible con versiones viejas y nuevas)
    for h in historial:
        # Si el historial viene como lista [usuario, bot]
        if isinstance(h, (list, tuple)):
            mensajes.append({"role": "user", "content": h[0]})
            mensajes.append({"role": "assistant", "content": h[1]})
        # Si viene como diccionario (versiones más nuevas)
        elif isinstance(h, dict):
            mensajes.append(h)
    
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

# 3. Interfaz corregida (SIN el argumento 'type')
demo = gr.ChatInterface(
    fn=chat_adia, 
    title="ADIA: Advanced Digital Intelligence Assistant"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
