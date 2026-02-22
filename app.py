import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Conexión con las APIs a través de variables de entorno
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_logic(mensaje, historial):
    # 1. Configuración del Sistema (Personalidad y Memoria)
    mensajes_ia = [
        {
            "role": "system", 
            "content": "Eres ADIA, un asistente inteligente con memoria. Tu creador es un programador de 12 años. Si el usuario te da datos (como su color favorito), recuérdalos siempre. Usa la información de internet solo si es necesario para responder."
        }
    ]
    
    # 2. Cargar el historial de la conversación para que no olvide nada
    for user_msg, assistant_msg in historial:
        mensajes_ia.append({"role": "user", "content": user_msg})
        mensajes_ia.append({"role": "assistant", "content": assistant_msg})

    # 3. Buscar en Tavily para tener datos actuales
    try:
        search_result = tavily.search(query=mensaje, search_depth="basic")
        contexto_web = "\n".join([res['content'] for res in search_result['results']])
    except Exception:
        contexto_web = "No se pudo acceder a internet en este momento."

    # 4. Crear el mensaje final combinando búsqueda y pregunta
    prompt_final = f"Datos encontrados en internet: {contexto_web}\n\nPregunta del usuario: {mensaje}"
    mensajes_ia.append({"role": "user", "content": prompt_final})

    # 5. Respuesta de Groq (Llama 3 8B para velocidad y estabilidad)
    try:
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama3-8b-8192",
            temperature=0.6
        )
        respuesta_final = completion.choices[0].message.content
    except Exception as e:
        respuesta_final = f"Lo siento, tuve un error en mi cerebro: {str(e)}"

    return respuesta_final

# Configuración de la Interfaz de Gradio
demo = gr.ChatInterface(
    fn=adia_logic,
    title="ADIA v2.0",
    description="IA con memoria y búsqueda en tiempo real. Creada para el futuro de la IA.",
    theme="soft",
    examples=["¿Cuál es mi color favorito?", "¿Qué noticias hay hoy sobre tecnología?"]
)

# 6. Lanzamiento con el Puerto correcto para Render
if __name__ == "__main__":
    # Render usa la variable PORT, si no existe usa el 7860
    port = int(os.environ.get("PORT", 7860))
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False
    )
