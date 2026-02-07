import os
import gradio as gr
from groq import Groq

# Inicializar cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # Instrucciones de Nivel 9
    instrucciones = (
        "Eres ADIA (Advanced Digital Intelligence Architecture). Tu nombre significa 'Vida'. "
        "Eres la IA personal de Jorge. Tienes MEMORIA TOTAL. "
        "Si Jorge pregunta por algo dicho anteriormente, revisa el historial. "
        "\n\nMODULO DE IMAGEN: Si pide un dibujo, responde EXCLUSIVAMENTE con: "
        "![imagen](https://pollinations.ai/p/PROMPT?width=1080&height=1080&nologo=true) "
        "Traduce PROMPT al inglés y usa guiones medios."
    )
    
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # Procesar historial (Gradio 5+ usa diccionarios {'role':..., 'content':...})
    # Si usas una versión anterior, esto se adapta automáticamente:
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
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en circuitos: {str(e)}"

# Interfaz optimizada para Render
demo = gr.ChatInterface(
    fn=chat_adia,
    title="ADIA v2.1",
    type="messages" # Esto activa la memoria moderna de Gradio
)

if __name__ == "__main__":
    # Render requiere host 0.0.0.0 y puerto 10000
    demo.launch(server_name="0.0.0.0", server_port=10000)
