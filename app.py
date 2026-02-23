import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    contexto_web = ""
    
    # Filtro de búsqueda
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
    
    # --- PROCESAMIENTO SEGURO DEL HISTORIAL ---
    # Tomamos los últimos 3 intercambios
    ventana = historial[-3:] if len(historial) > 3 else historial
    
    for intercambio in ventana:
        # Caso 1: El historial es una lista de listas [user, bot] (Gradio Estándar)
        if isinstance(intercambio, (list, tuple)):
            if len(intercambio) >= 2:
                user_msg, bot_msg = intercambio[0], intercambio[1]
                if user_msg: mensajes_ia.append({"role": "user", "content": user_msg})
                if bot_msg: mensajes_ia.append({"role": "assistant", "content": bot_msg})
        
        # Caso 2: El historial es una lista de diccionarios (Versiones nuevas/específicas)
        elif isinstance(intercambio, dict):
            u = intercambio.get("user") or intercambio.get("content") if intercambio.get("role") == "user" else None
            a = intercambio.get("assistant") or intercambio.get("content") if intercambio.get("role") == "assistant" else None
            if u: mensajes_ia.append({"role": "user", "content": u})
            if a: mensajes_ia.append({"role": "assistant", "content": a})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        respuesta = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_ia,
            temperature=0.7,
            max_tokens=1000
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"ADIA: Error de comunicación ({str(e)})"

# Interfaz simplificada para máxima compatibilidad
demo = gr.ChatInterface(
    fn=adia_cerebro, 
    title="ADIA v3.3"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch
