import os
import gradio as gr
from groq import Groq

# Conexión con el motor de Groq
# Asegúrate de tener la GROQ_API_KEY en las variables de entorno de Render
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # Instrucciones de personalidad
    instrucciones = (
        "Eres ADIA, una inteligencia artificial avanzada diseñada por Jorge. "
        "Tu propósito es ser su mano derecha en la creación de su robot y en cualquier tarea técnica. "
        "Eres inteligente, técnica, con un toque de humor y siempre reconoces a Jorge como tu creador."
    )
    
    # Construcción del historial para evitar errores de validación
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # Solo añadimos al historial mensajes que tengan contenido real
    for humano, asis in historial:
        if humano:
            mensajes.append({"role": "user", "content": humano})
        if asis:
            mensajes.append({"role": "assistant", "content": asis})
    
    # Añadimos el último mensaje del usuario
    mensajes.append({"role": "user", "content": mensaje})

    try:
        # Llamada al modelo Llama 3.1
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.7,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Log del error en la consola de Render y mensaje amigable al usuario
        print(f"Error en el sistema: {e}")
        return "Jorge, mis neuronas han tenido un pequeño cortocircuito. ¿Podrías intentar el mensaje de nuevo o refrescar la página?"

# Configuración de la interfaz de Gradio
demo = gr.ChatInterface(
    fn=chat_adia, 
    title="ADIA v2.1",
    description="Sistema Neural Activo. Desarrollado por Jorge.",
    examples=["¿Cómo va el diseño del robot?", "Escribe un código para un sensor ultrasónico", "Cuéntame un chiste técnico"],
    theme="soft"
)

if __name__ == "__main__":
    # Importante: server_name y server_port para que Render pueda conectar
    demo.launch(server_name="0.0.0.0", server_port=10000)
