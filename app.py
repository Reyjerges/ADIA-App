import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes con variables de entorno de Render
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda con Tavily (Solo si es necesario para ahorrar tiempo)
    contexto_web = ""
    if any(p in mensaje.lower() for p in ["noticia", "quién", "qué pasó", "hoy", "precio"]):
        try:
            search_result = tavily.search(query=mensaje, search_depth="basic", max_results=2)
            for r in search_result.get('results', []):
                # Tomamos una buena porción de la noticia
                contexto_web += f"DATO: {r['content'][:600]}\n"
        except:
            contexto_web = "No pude acceder a internet en este momento."

    # 2. Personalidad Profesional (ChatGPT Style)
    sistema_prompt = (
        "Eres ADIA, un asistente de IA profesional y eficiente. Jorge es tu prioridad. "
        "Tu tono es formal y directo. Usa el contexto de internet para informar con precisión. "
        f"CONTEXTO ACTUAL: {contexto_web}"
    )

    # 3. Memoria Manual Blindada
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Enviamos los últimos 6 mensajes (3 vueltas de conversación)
    for usuario, bot in historial[-6:]:
        if usuario: mensajes_ia.append({"role": "user", "content": usuario})
        if bot: mensajes_ia.append({"role": "assistant", "content": bot})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # USAMOS EL SEGUNDO MODELO MÁS POTENTE Y EL MÁS ESTABLE
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=mensajes_ia,
            temperature=0.6
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"ADIA: Error de comunicación. Intenta de nuevo. ({str(e)})"

# 4. Interfaz Limpia para Render (Sin argumentos conflictivos)
with gr.Blocks() as demo:
    gr.Markdown("# ADIA - Inteligencia Equilibrada")
    gr.ChatInterface(fn=adia_cerebro)

if __name__ == "__main__":
    # Render maneja el puerto
    puerto = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
