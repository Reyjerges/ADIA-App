import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Conexión con las APIs (Configúralas en el Dashboard de Render)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_logic(mensaje, historial):
    # 1. Personalidad de ADIA
    mensajes_ia = [
        {
            "role": "system", 
            "content": "Eres ADIA, una IA con memoria creada por un programador de 12 años. Si el usuario te cuenta algo personal, recuérdalo. Eres directo y eficiente."
        }
    ]
    
    # 2. Cargar historial para la memoria
    for user_msg, assistant_msg in historial:
        mensajes_ia.append({"role": "user", "content": user_msg})
        mensajes_ia.append({"role": "assistant", "content": assistant_msg})

    # 3. Búsqueda en tiempo real con Tavily
    try:
        search_result = tavily.search(query=mensaje, search_depth="basic")
        contexto_web = "\n".join([res['content'] for res in search_result['results']])
    except Exception:
        contexto_web = "No se pudo obtener información de internet."

    # 4. Prompt final
    prompt_final = f"Datos de internet: {contexto_web}\n\nPregunta: {mensaje}"
    mensajes_ia.append({"role": "user", "content": prompt_final})

    # 5. Respuesta de Groq (Llama 3 8B)
    try:
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama3-8b-8192",
            temperature=0.7
        )
        respuesta = completion.choices[0].message.content
    except Exception as e:
        respuesta = f"Error en el sistema: {str(e)}"

    return respuesta

# Configuración de la Interfaz (Corregida para evitar error de 'theme')
demo = gr.ChatInterface(
    fn=adia_logic,
    title="ADIA v2.0",
    description="IA con memoria y búsqueda real. Creada por un Hechicero de Grado Especial.",
    examples=["¿Quién es más fuerte, tú o ChatGPT?", "¿Cuál es mi color favorito?"]
)

# Lanzamiento con puerto dinámico para Render
if __name__ == "__main__":
    # Definimos el puerto antes del launch
    puerto = int(os.environ.get("PORT", 7860))
    
    # Aplicamos el tema de forma segura fuera del constructor
    demo.theme = gr.themes.Soft()
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=puerto,
        share=False
    )
