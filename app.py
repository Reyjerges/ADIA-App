import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    contexto_web = ""
    
    # Búsqueda inteligente
    if len(mensaje.split()) > 3:
        try:
            search_result = tavily.search(query=mensaje, search_depth="basic", max_results=1)
            contexto_web = search_result['results'][0]['content'] if search_result['results'] else ""
        except:
            contexto_web = ""

    mensajes_ia = [{
        "role": "system", 
        "content": f"Eres ADIA. Inteligencia de Grado Especial. Natural y lógica. Contexto: {contexto_web}"
    }]
    
    # Procesamiento del historial
    ventana = historial[-3:] if len(historial) > 3 else historial
    for intercambio in ventana:
        if isinstance(intercambio, (list, tuple)) and len(intercambio) >= 2:
            u, a = intercambio[0], intercambio[1]
            if u: mensajes_ia.append({"role": "user", "content": u})
            if a: mensajes_ia.append({"role": "assistant", "content": a})
        elif isinstance(intercambio, dict):
            u = intercambio.get("user") or intercambio.get("content")
            a = intercambio.get("assistant") or intercambio.get("content")
            if u: mensajes_ia.append({"role": "user", "content": u})
            if a: mensajes_ia.append({"role": "assistant", "content": a})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        respuesta = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_ia,
            temperature=0.7
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"ADIA: Error ({str(e)})"

# Interfaz
demo = gr.ChatInterface(fn=adia_cerebro, title="ADIA v3.4")

if __name__ == "__main__":
    # Render usa la variable PORT. Si no existe, usamos 10000 por defecto.
    port = int(os.environ.get("PORT", 10000))
    # 'prevent_thread_lock=False' es clave para que el proceso no muera en Render
    demo.launch(
        server_name="0.0.0.0", 
        server_port=port,
        prevent_thread_lock=False
    )
