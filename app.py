import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Conexión con las APIs
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_logic(mensaje, historial):
    # 1. Identidad de la IA
    mensajes_ia = [
        {"role": "system", "content": "Eres ADIA, una IA avanzada con memoria. Ayuda de forma precisa y recuerda datos personales que el usuario comparta."}
    ]
    
    # 2. Memoria (Historial)
    for user_msg, assistant_msg in historial[-5:]:
        mensajes_ia.append({"role": "user", "content": user_msg})
        mensajes_ia.append({"role": "assistant", "content": assistant_msg})

    # 3. Búsqueda Web
    try:
        search_result = tavily.search(query=mensaje, search_depth="basic")
        contexto_web = "\n".join([res['content'] for res in search_result['results']])[:800]
    except:
        contexto_web = "Sin datos de internet."

    # 4. Prompt Final
    prompt_final = f"Internet: {contexto_web}\n\nPregunta: {mensaje}"
    mensajes_ia.append({"role": "user", "content": prompt_final})

    # 5. Respuesta de Groq
    try:
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama-3.1-8b-instant",
            temperature=0.6,
            max_tokens=500
        )
        respuesta = completion.choices[0].message.content
    except Exception as e:
        respuesta = f"Error: {str(e)}"

    return respuesta

# Interfaz de Usuario (Líneas 50-65 donde estaba el error)
demo = gr.ChatInterface(
    fn=adia_logic,
    title="ADIA v2.2",
    description="IA con memoria y búsqueda activa."
)

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 7860))
    demo.theme = gr.themes.Soft()
    demo.launch(
        server_name="0.0.0.0",
        server_port=puerto,
        share=False
    )
