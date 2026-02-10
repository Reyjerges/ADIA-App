import gradio as gr
from groq import Groq
import os

# Configuración simple
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_chat(mensaje, historial):
    # Crear la lista de mensajes con el formato exacto que pide Groq
    mensajes_ia = [{"role": "system", "content": "Eres ADIA v1.2, asistente de ingeniería."}]
    
    # Convertir el historial de Gradio al formato de Groq
    for usuario, bot in historial:
        if usuario:
            mensajes_ia.append({"role": "user", "content": str(usuario)})
        if bot:
            mensajes_ia.append({"role": "assistant", "content": str(bot)})
    
    # Añadir el mensaje nuevo
    mensajes_ia.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_ia
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Interfaz mínima
app = gr.ChatInterface(
    fn=adia_chat,
    title="ADIA v1.2",
    description="Sistema de chat simplificado para evitar errores de formato."
)

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=10000)
    
    
