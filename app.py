import os
import gradio as gr
from groq import Groq

# Configuración del cliente con manejo de error si no hay API KEY
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

def chat_adia(mensaje, historial):
    instrucciones = (
        "Eres ADIA, una IA nivel 9. Tu nombre significa 'Vida'. "
        "Tienes MEMORIA TOTAL de esta charla. Si Jorge pregunta algo pasado, revísalo. "
        "\n\nMODULO DE IMAGEN: Si pide un dibujo, usa: "
        "![imagen](https://pollinations.ai/p/PROMPT?width=1080&height=1080&nologo=true)"
    )
    
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # Este bucle es compatible con versiones antiguas y nuevas de Gradio
    for h in historial:
        # Si el historial viene como lista de listas [user, bot]
        if isinstance(h, (list, tuple)):
            mensajes.append({"role": "user", "content": h[0]})
            mensajes.append({"role": "assistant", "content": h[1]})
        # Si viene como diccionario (Gradio 5)
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
        return f"ADIA: Error de conexión. Verifica la API KEY. Detalle: {str(e)}"

# Interfaz estándar sin decoraciones extra para evitar fallos de Deploy
demo = gr.ChatInterface(fn=chat_adia, title="ADIA v2.2")

if __name__ == "__main__":
    # Render requiere obligatoriamente el puerto 10000
    demo.launch(server_name="0.0.0.0", server_port=10000)
