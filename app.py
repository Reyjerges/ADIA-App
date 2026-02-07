import os
import gradio as gr
from groq import Groq

# Configuración del cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # Instrucción básica
    mensajes = [{"role": "system", "content": "Eres ADIA, creada por Jorge."}]
    
    # Agregar historial solo si existe y es válido
    for h in historial:
        if len(h) == 2:
            mensajes.append({"role": "user", "content": h[0]})
            mensajes.append({"role": "assistant", "content": h[1]})
    
    # Agregar el mensaje actual
    mensajes.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return "Error de conexión. Jorge, intenta refrescar la página."

# Interfaz mínima para evitar errores de compatibilidad
demo = gr.ChatInterface(fn=chat_adia, title="ADIA")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
    
