import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda de noticias / información real
    contexto_web = "No se encontró información reciente."
    try:
        # Forzamos una búsqueda más profunda para noticias
        search_result = tavily.search(query=mensaje, search_depth="advanced", max_results=3)
        if search_result['results']:
            contexto_web = "\n".join([f"NOTICIA: {r['content']}" for r in search_result['results']])
    except Exception as e:
        print(f"Error en Tavily: {e}")

    # 2. Instrucciones del Sistema (Más estrictas)
    # Le decimos que DEBE usar el contexto de arriba
    sistema = (
        "Eres ADIA, una IA de Grado Especial. Jorge es tu prioridad. "
        "REGLA DE ORO: Tienes acceso a internet. Usa la información del 'Contexto' para responder. "
        "Si te preguntan por noticias, lee el Contexto y resume lo que dice. "
        f"CONTEXTO ACTUAL DE INTERNET: {contexto_web}"
    )

    mensajes_ia = [{"role": "system", "content": sistema}]
    
    # 3. MEMORIA CORREGIDA (Para que no se le olvide nada)
    # Gradio manda el historial como una lista de listas [[user, bot], [user, bot]]
    for par in historial:
        if len(par) == 2:
            user_msg, bot_msg = par
            if user_msg: mensajes_ia.append({"role": "user", "content": user_msg})
            if bot_msg: mensajes_ia.append({"role": "assistant", "content": bot_msg})
    
    # Añadimos el mensaje actual
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # Usamos el 70B que es el que mejor procesa noticias
        respuesta = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_ia,
            temperature=0.5 # Menos creatividad, más hechos
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"ADIA: Error de procesamiento ({str(e)})"

# Interfaz
demo = gr.ChatInterface(
    fn=adia_cerebro, 
    title="ADIA v3.5 - Real Time",
    description="Sistema de búsqueda profunda y memoria activa."
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=port, prevent_thread_lock=False)
