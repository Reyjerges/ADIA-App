import os
import gradio as gr
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_chat(mensaje, historial):
    # 1. El System Prompt siempre es la base
    mensajes_ia = [
        {"role": "system", "content": "Eres ADIA. Inteligencia de alto nivel. Tienes memoria absoluta de esta conversación con Jorge. Sé directa y brutalmente eficiente."}
    ]
    
    # 2. Inyectamos TODO el historial previo en el contexto
    # Gradio pasa el historial como una lista de listas [[user, bot], [user, bot]]
    for interaccion in historial:
        mensajes_ia.append({"role": "user", "content": interaccion[0]})
        mensajes_ia.append({"role": "assistant", "content": interaccion[1]})
    
    # 3. Añadimos el mensaje que acabas de escribir
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama-3.3-70b-versatile",
            temperature=0.5 # Subimos un poco para que sea más fluida en la conversación
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error de memoria: {str(e)}"

# Usamos ChatInterface que maneja el historial automáticamente por nosotros
demo = gr.ChatInterface(
    fn=adia_chat, 
    title="ADIA",
    description="Memoria Activa - Inteligencia Superior"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
