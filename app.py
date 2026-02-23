import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda rápida (Solo si es necesario para ahorrar tiempo)
    contexto_web = ""
    palabras_clave = ["noticias", "quién es", "qué pasó", "hoy", "precio"]
    
    # Solo busca en internet si el mensaje parece una consulta de actualidad
    if any(palabra in mensaje.lower() for palabra in palabras_clave):
        try:
            search_result = tavily.search(query=mensaje, search_depth="basic", max_results=2)
            for r in search_result.get('results', []):
                contexto_web += f"DATO: {r['content']}\n"
        except:
            pass

    # 2. El Prompt Profesional
    sistema_prompt = (
        "Eres ADIA, asistente profesional de Jorge. "
        "REGLA: Usa el historial para recordar datos personales de Jorge. "
        f"CONTEXTO WEB: {contexto_web}"
    )

    # 3. CORRECCIÓN DE MEMORIA (Gradio envía historial como lista de listas)
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Este bucle es el que fallaba. Ahora extrae correctamente Usuario y Bot.
    for mensaje_usuario, respuesta_bot in historial:
        if mensaje_usuario:
            mensajes_ia.append({"role": "user", "content": mensaje_usuario})
        if respuesta_bot:
            mensajes_ia.append({"role": "assistant", "content": respuesta_bot})
    
    # Añadimos la pregunta de ahora
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # Llama 3.3 70B Versatile
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_ia,
            temperature=0.4 # Más estable para recordar
        )
        return completion.choices.message.content
    except Exception as e:
        return f"ADIA: Error de conexión. (Límite de mensajes alcanzado o error de red)."

# 4. Interfaz sin 'type' y sin 'theme' dentro (para evitar TypeErrors)
with gr.Blocks() as demo:
    gr.Markdown("# ADIA v3.6 - Memoria Corregida")
    gr.ChatInterface(fn=adia_cerebro)

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
