import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Conexión con las APIs
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_logic(mensaje, historial):
    # 1. Definición de identidad
    mensajes_ia = [
        {
            "role": "system", 
            "content": "Eres ADIA, una inteligencia artificial avanzada con capacidad de memoria. Tu objetivo es ayudar al usuario de forma precisa. Si el usuario te da información personal, recuérdala para el futuro."
        }
  ]
    
    # 2. Gestión del historial (Memoria)
    # Limitamos a los últimos 5 mensajes para no saturar la memoria
    for user_msg, assistant_msg in historial[-5:]:
        mensajes_ia.append({"role": "user", "content": user_msg})
        mensajes_ia.append({"role": "assistant", "content": assistant_msg})

    # 3. Búsqueda web limitada para evitar errores de saturación
    try:
        search_result = tavily.search(query=mensaje, search_depth="basic")
        # Solo tomamos una parte del contenido para que no de error de tamaño
        contexto_web = "\n".join([res['content'] for res in search_result['results']])[:800]
    except Exception:
        contexto_web = "Información web no disponible en este momento."

    # 4. Construcción del mensaje final
    prompt_final = f"Datos recientes: {contexto_web}\n\nPregunta: {mensaje}"
    mensajes_ia.append({"role": "user", "content": prompt_final})

    # 5. Respuesta de Groq con modelo estable
    try:
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama-3.1-8b-instant",
            temperature=0.6,
            max_tokens=500 # Limitamos la respuesta para mayor velocidad
        )
        respuesta = completion.choices[0].message.content
    except Exception as e:
        respuesta = f"ADIA ha encontrado un problema técnico: {str(e)}"

    return respuesta

# Interfaz de Usuario
demo = gr.ChatInterface(
    fn=adia_logic,
    title="ADIA v2
