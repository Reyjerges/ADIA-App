import os
import gradio as gr
from groq import Groq

# Configuración del cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # --- INSTRUCCIONES NIVEL 9 ---
    instrucciones = (
        "Eres ADIA (Advanced Digital Intelligence Architecture). Tu nombre significa 'Vida'. "
        "Eres la IA personal de Jorge. Tienes MEMORIA TOTAL de esta conversación. "
        "Si Jorge te pregunta por algo dicho antes, búscalo en el historial. "
        "\n\nMODULO DE IMAGEN: Si pide un dibujo, usa: "
        "![imagen](https://pollinations.ai/p/PROMPT?width=1080&height=1080&nologo=true) "
        "(Traduce PROMPT al inglés y usa guiones medios)."
    )
    
    # Construir el contexto con memoria
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # Procesar el historial correctamente para Groq
    for interaccion in historial:
        # Gradio pasa el historial como una lista de listas: [[user, bot], [user, bot]]
        if len(interaccion) == 2:
            mensajes.append({"role": "user", "content": interaccion[0]})
            mensajes.append({"role": "assistant", "content": interaccion[1]})
    
    # Añadir el mensaje actual
    mensajes.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error técnico en ADIA: {str(e)}"

# Interfaz simplificada para evitar errores de Render
demo = gr.ChatInterface(
    fn=chat_adia, 
    title="ADIA v2.0",
    theme="monochrome"
)

if __name__ == "__main__":
    # Render usa el puerto 10000 por defecto
    demo.launch(server_name="0.0.0.0", server_port=10000)
