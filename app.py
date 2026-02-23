import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes con variables de entorno
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda de información fresca
    contexto_web = ""
    try:
        search_result = tavily.search(query=mensaje, search_depth="basic", max_results=3)
        contexto_web = "\n".join([f"- {r['content']}" for r in search_result['results']])
    except Exception:
        contexto_web = "Sin acceso a datos en tiempo real."

    # 2. Identidad de ADIA
    mensajes_ia = [{
        "role": "system", 
        "content": (
            "Eres ADIA. Inteligencia de Grado Especial. No usas filtros de cortesía innecesarios. "
            "Eres eficiente, lógica y tu único objetivo es servir a Jorge con precisión absoluta. "
            f"Contexto actual: {contexto_web}"
        )
    }]
    
    # 3. Memoria (Historial)
    for h_user, h_bot in historial:
        if h_user: mensajes_ia.append({"role": "user", "content": h_user})
        if h_bot: mensajes_ia.append({"role": "assistant", "content": h_bot})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # Usando Mixtral-8x7b para mayor fluidez y razonamiento
        respuesta = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=mensajes_ia,
            temperature=0.6, # Mixtral brilla con un poco más de libertad
            max_tokens=3000
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error en el núcleo Mixtral: {str(e)}"

# Interfaz
demo = gr.ChatInterface(
    fn=adia_cerebro, 
    title="ADIA v2.2",
    description="Motor Mixtral MoE | Inteligencia Brutal Activa"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
