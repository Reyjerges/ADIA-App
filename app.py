import os
import gradio as gr
from groq import Groq

# 1. Configuración del Cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    instrucciones = (
        "Eres ADIA, una inteligencia artificial experta en física y robótica. "
        "Fuiste creada por un ingeniero de 7mo grado. Eres inteligente, "
        "curiosa y siempre das respuestas técnicas pero fáciles de entender."
    )
    
    # Preparamos la estructura de mensajes
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # Formateo del Historial para evitar errores en mensajes sucesivos
    for usuario, asistente in historial:
        if usuario:
            mensajes.append({"role": "user", "content": usuario})
        if asistente:
            mensajes.append({"role": "assistant", "content": asistente})
    
    # Añadimos el mensaje actual del usuario
    mensajes.append({"role": "user", "content": mensaje})

    try:
        # 2. Llamada a la API (Revisado que todos los paréntesis cierren)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    
    except Exception as e:
        return f"ADIA reporta un error técnico: {str(e)}"

# 3. Interfaz de Usuario de Gradio
demo = gr.ChatInterface(
    fn=responder_adia,
    title="PROYECTO ADIA",
    description="IA Experta en Física y Robótica Avanzada",
)

# 4. Lanzamiento del servidor para Render
if __name__ == "__main__":
    # Obtenemos el puerto de Render o usamos el 7860 por defecto
    puerto = int(os.environ.get("PORT", 7860))
    
    demo.launch(
        server_name="0.0.0.0", 
        server_port=puerto,
        share=False
    )
