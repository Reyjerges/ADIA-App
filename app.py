import os
from dotenv import load_dotenv
import gradio as gr
from groq import Groq

# Cargar variables de entorno
load_dotenv()

# Validar API Key
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY no está configurada")

client = Groq(api_key=api_key)

def chat_adia(mensaje, historial):
    """Función de chat con ADIA."""
    
    # Validar historial
    if historial is None:
        historial = []
    
    instrucciones = (
        "Eres ADIA (Advanced Digital Intelligence Architecture). Tu nombre significa 'Vida'. "
        "Eres la IA personal de Jorge. Tienes MEMORIA TOTAL. "
        "Si Jorge pregunta por algo dicho anteriormente, revisa el historial. "
        "\n\nMODULO DE IMAGEN: Si pide un dibujo, responde EXCLUSIVAMENTE con: "
        "![imagen](https://pollinations.ai/p/PROMPT?width=1080&height=1080&nologo=true) "
        "Traduce PROMPT al inglés y usa guiones medios."
    )
    
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # Procesar historial
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

# ✅ SIN el parámetro type="messages"
demo = gr.ChatInterface(
    fn=chat_adia,
    title="ADIA v2.1"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
           
