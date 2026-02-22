import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Conexión con las APIs
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_logic(mensaje, historial):
    # 1. Definición de identidad y memoria
    mensajes_ia = [
        {
            "role": "system", 
            "content": "Eres ADIA, una inteligencia artificial avanzada con capacidad de memoria. Tu objetivo es ayudar al usuario de forma precisa y eficiente. Si el usuario te proporciona información personal o preferencias, guárdalas en el contexto para futuras respuestas."
        }
    ]
    
    # 2. Gestión del historial de conversación
    for user_msg, assistant_msg in historial:
        mensajes_ia.append({"role": "user", "content": user_msg})
        mensajes_ia.append({"role": "assistant", "content": assistant_msg})

    # 3. Búsqueda de información actualizada
    try:
        search_result = tavily.search(query=mensaje, search_depth="basic")
        contexto_web = "\n".join([res['content'] for res in search_result['results']])
    except Exception:
        contexto_web = "Búsqueda web no disponible."

    # 4. Construcción del prompt
    prompt_final = f"Contexto de búsqueda: {contexto_web}\n\nPregunta del usuario: {mensaje}"
    mensajes_ia.append({"role": "user", "content": prompt_final})

    # 5. Respuesta de Groq con el modelo actualizado (Llama 3.1 8B)
    try:
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama-3.1-8b-instant",
            temperature=0.7
        )
        respuesta = completion.choices[0].message.content
    except Exception as e:
        respuesta = f"Error en el procesamiento: {str(e)}"

    return respuesta

# Interfaz de Usuario
demo = gr.ChatInterface(
    fn=adia_logic,
    title="ADIA v2.1",
    description="Asistente inteligente con memoria y acceso a información en tiempo real.",
    examples=["¿Cuál es la noticia más importante de hoy?", "¿Puedes recordar mi nombre si te lo digo?"]
)

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 7860))
    demo.theme = gr.themes.Soft()
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=puerto,
        share=False
    )
