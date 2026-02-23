import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    contexto_web = ""
    
    # Filtro inteligente para búsquedas
    if len(mensaje.split()) > 3:
        try:
            search_result = tavily.search(query=mensaje, search_depth="basic", max_results=1)
            contexto_web = search_result['results'][0]['content'] if search_result['results'] else ""
        except:
            contexto_web = ""

    mensajes_ia = [{
        "role": "system", 
        "content": (
            "Eres ADIA. Asistente De Inteligencia Artificial. "
            "Responde de forma natural, lógica y sofisticada a Jorge. "
            f"Contexto: {contexto_web}"
        )
    }]
    
    # --- FIX PARA EL ERROR DE UNPACKING ---
    # Procesamos el historial de forma segura sin importar el formato
    ventana = historial[-3:] if len(historial) > 3 else historial
    for intercambio in ventana:
        # Si es un diccionario (Gradio nuevo)
        if isinstance(intercambio, dict):
            mensajes_ia.append({"role": "user", "content": intercambio.get("user", "")})
            mensajes_ia.append({"role": "assistant", "content": intercambio.get("assistant", "")})
        # Si es una lista/tupla (Gradio antiguo)
        elif isinstance(intercambio, (list, tuple)) and len(intercambio) == 2:
            user_msg, bot_msg = intercambio
            if user_msg: mensajes_ia.append({"role": "user", "content": user_msg})
            if bot_msg: mensajes_ia.append({"role": "assistant", "content": bot_msg})
    
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
        return f"ADIA: Error en el núcleo ({str(e)})"

# Interfaz
demo = gr.ChatInterface(
    fn=adia_cerebro, 
    title="ADIA v3.2",
    type="messages" # Forzamos el formato de mensajes más estable
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
