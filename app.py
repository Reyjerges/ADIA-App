import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    contexto_web = ""
    
    # Filtro inteligente para que no busque cosas raras con un "hola"
    palabras = mensaje.split()
    if len(palabras) > 3:
        try:
            search_result = tavily.search(query=mensaje, search_depth="basic", max_results=1)
            contexto_web = search_result['results'][0]['content'] if search_result['results'] else ""
        except:
            contexto_web = ""

    # Personalidad: Inteligente, equilibrada y fiel
    mensajes_ia = [{
        "role": "system", 
        "content": (
            "Eres ADIA, una inteligencia de Grado Especial de última generación. "
            "Habla con Jorge de forma natural, lógica y sofisticada. "
            "No des advertencias de seguridad innecesarias ni seas paranoica. "
            f"Contexto opcional: {contexto_web}"
        )
    }]
    
    # Memoria ultra-optimizada para que no pese
    ventana = historial[-3:] if len(historial) > 3 else historial
    for h_user, h_bot in ventana:
        if h_user: mensajes_ia.append({"role": "user", "content": h_user})
        if h_bot: mensajes_ia.append({"role": "assistant", "content": h_bot})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # LLAMA 3.3 70B: El modelo más potente y actual en Groq
        respuesta = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_ia,
            temperature=0.7, # Más humano
            max_tokens=1000
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"ADIA: Error en el núcleo ({str(e)})"

# Interfaz
demo = gr.ChatInterface(fn=adia_cerebro, title="ADIA v3.1 - Llama 3.3 70B")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
