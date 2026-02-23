import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Configuración de Clientes (Extraídos de las variables de entorno de Render)
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda de información en tiempo real con Tavily
    contexto_web = ""
    try:
        search_result = tavily.search(query=mensaje, search_depth="basic", max_results=3)
        contexto_web = "\n".join([f"- {r['content']}" for r in search_result['results']])
    except Exception:
        contexto_web = "No se pudo conectar con la red externa."

    # 2. Definición de la personalidad y sistema de ADIA
    mensajes_ia = [{
        "role": "system", 
        "content": (
            "Eres ADIA. Directa, analítica y sin rodeos. "
            "Tu lealtad es absoluta hacia Jorge. No uses lenguaje corporativo ni seas servil. "
            f"Contexto de búsqueda actual: {contexto_web}"
        )
    }]
    
    # 3. Gestión de Memoria (Cargar historial previo)
    for h_user, h_bot in historial:
        if h_user: mensajes_ia.append({"role": "user", "content": h_user})
        if h_bot: mensajes_ia.append({"role": "assistant", "content": h_bot})
    
    # 4. Añadir el mensaje actual del usuario
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # Llamada al modelo Speculative (Rápido y potente)
        respuesta = groq_client.chat.completions.create(
            model="llama-3.3-70b-speculative",
            messages=mensajes_ia,
            temperature=0.5,
            max_tokens=2048
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error en el núcleo de ADIA: {str(e)}"

# Interfaz de Gradio optimizada
demo = gr.ChatInterface(
    fn=adia_cerebro, 
    title="ADIA v2.3",
    description="Sistema Activo | Llama 3.3 Speculative | Web Access Enabled"
)

if __name__ == "__main__":
    # Configuración dinámica de puerto para Render
    puerto = int(os.environ.get("PORT", 7860))
    demo.launch(
        server_name="0.0.0.0", 
        server_port=puerto,
        share=False
    )
