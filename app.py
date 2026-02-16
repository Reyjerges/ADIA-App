import os
import gradio as gr
from groq import Groq

# 1. Configuración del Cliente
# Render leerá la clave desde las variables de entorno
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    # Definimos la personalidad de ADIA
    instrucciones = (
        "Eres ADIA, una inteligencia artificial experta en física y robótica. "
        "Fuiste creada por un ingeniero de 7mo grado. Eres inteligente, "
        "curiosa y siempre das respuestas técnicas pero fáciles de entender."
    )
    
    # Preparamos la estructura de mensajes para Groq
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # 2. Formateo del Historial (Para evitar el error del segundo mensaje)
    # Gradio pasa el historial como una lista de listas [[user, bot], [user, bot]]
    for usuario, asistente in historial:
        if usuario:
            mensajes.append({"role": "user", "content": usuario})
        if asistente:
            mensajes.append({"role": "assistant", "content": asistente})
    
    # Añadimos el mensaje actual
    mensajes.append({"role": "user", "content": mensaje})

    try:
        # 3. Llamada a la API con el modelo actualizado
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    
    except Exception as e:
        # Esto nos dirá el error real en el chat si algo falla
        return f"Error de conexión: {str(e)}"

# 4. Interfaz de Usuario
demo = gr.ChatInterface(
