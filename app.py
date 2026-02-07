import os
import gradio as gr
from groq import Groq

# Configuración del cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # Instrucciones precisas para que la imagen aparezca EN EL CHAT
    instrucciones = (
        "Eres ADIA, la IA de Jorge. "
        "Si Jorge te pide una imagen o dibujo, genera la respuesta siguiendo este formato EXACTO: "
        "![descripción](https://image.pollinations.ai/prompt/PROMPT?width=1024&height=1024&nologo=true&seed=42) "
        "\n\nREGLAS PARA LA IMAGEN:"
        "\n1. Traduce el pedido de Jorge al inglés."
        "\n2. Cambia los espacios por guiones medios (-) en el PROMPT."
        "\n3. NO escribas nada más, solo el formato ![imagen](url)."
    )
    
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # Manejo de memoria para Gradio
    for h in historial:
        if isinstance(h, dict):
            mensajes.append(h)
        else:
            mensajes.append({"role": "user", "content": h[0]})
            mensajes.append({"role": "assistant", "content": h[1]})
            
    mensajes.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.6
        )
        respuesta = completion.choices[0].message.content
        return respuesta
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# Configuración de la interfaz para Render
demo = gr.ChatInterface(
    fn=chat_adia,
    title="ADIA - Inteligencia Digital",
    type="messages" # Esto es vital en las versiones nuevas de Gradio
)

if __name__ == "__main__":
    # Render requiere el puerto 10000 y host 0.0.0.0
    demo.launch(server_name="0.0.0.0", server_port=10000)
