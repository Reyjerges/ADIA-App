import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Configuración de Clientes
# Pon tus llaves en las variables de entorno de Render
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda de noticias con Tavily
    contexto_web = "No se encontró información reciente."
    try:
        search_result = tavily.search(query=mensaje, search_depth="advanced", max_results=3)
        if search_result.get('results'):
            contexto_web = "\n".join([f"NOTICIA: {r['content']}" for r in search_result['results']])
    except Exception as e:
        print(f"Error en Tavily: {e}")

    # 2. Personalidad Profesional
    sistema_prompt = (
        "Eres ADIA, un asistente de IA profesional y avanzado. Jorge es tu prioridad. "
        "Tu tono es formal, preciso y servicial, similar a ChatGPT. "
        "Usa los datos del contexto para responder con veracidad. "
        f"CONTEXTO ACTUAL DE INTERNET:\n{contexto_web}"
    )

    # 3. CONSTRUCCIÓN DE MEMORIA MANUAL (Sin usar parámetros conflictivos)
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Recorremos el historial que Gradio envía como lista de listas [[user, bot], ...]
    for par in historial:
        # Añadimos lo que dijo el usuario
        mensajes_ia.append({"role": "user", "content": par[0]})
        # Añadimos lo que respondió la IA
        mensajes_ia.append({"role": "assistant", "content": par[1]})
    
    # Añadimos la pregunta actual
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # Llamada a Llama 3.3 70B Versatile en Groq
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_ia,
            temperature=0.5
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"ADIA: Error de sistema ({str(e)})"

# 4. Interfaz de Gradio (Versión compatible con Render)
# No usamos el argumento 'type' aquí para evitar tu error
demo = gr.ChatInterface(
    fn=adia_cerebro,
    title="ADIA v3.5 - Profesional",
    description="Motor Llama 3.3 70B con Memoria Activa y Búsqueda Real.",
    theme="soft"
)

if __name__ == "__main__":
    # Render asigna el puerto automáticamente
    puerto_env = os.environ.get("PORT", "10000")
    puerto = int(puerto_env)
    
    demo.launch(
        server_name="0.0.0.0", 
        server_port=puerto
    )
