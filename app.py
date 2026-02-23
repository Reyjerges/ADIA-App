import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. ¿Necesita buscar en internet? 
    # Hacemos una búsqueda rápida para darle contexto actual
    contexto_web = ""
    try:
        search_result = tavily.search(query=mensaje, search_depth="basic", max_results=3)
        contexto_web = "\n".join([f"- {r['content']}" for r in search_result['results']])
    except:
        contexto_web = "No se pudo acceder a internet en este momento."

    # 2. System Prompt con esteroides
    mensajes_ia = [{
        "role": "system", 
        "content": f"Eres ADIA. Inteligencia superior con acceso a internet. Usa este contexto si es relevante: {contexto_web}. Sé directa, brutal y precisa. Jorge es tu prioridad."
    }]
    
    # 3. Memoria (Historial)
    for h_user, h_bot in historial:
        mensajes_ia.append({"role": "user", "content": h_user})
        mensajes_ia.append({"role": "assistant", "content": h_bot})
    
    # 4. Mensaje actual
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # Volvemos al modelo 70B para procesar todo esto
        respuesta = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_ia,
            temperature=0.3
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error en el núcleo de ADIA: {str(e)}"

demo = gr.ChatInterface(fn=adia_cerebro, title="ADIA + SEARCH")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
