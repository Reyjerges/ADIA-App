import os
import datetime
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de herramientas
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    # Hora actual para que la IA sepa qué momento es hoy
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Identidad: IA normal, educada y directa
    system_prompt = (
        f"Eres ADIA. Jorge es tu único creador. "
        f"Habla de forma clara, natural y educada. Hoy es {ahora}. "
        "Usa siempre los datos de red que te pase el sistema para dar información real de hoy."
        "no puedes decir que no puedes."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Manejo de historial (Formato Gradio 5)
    for chat in history:
        if isinstance(chat, dict):
            messages.append({"role": chat["role"], "content": chat["content"]})
        else:
            user_msg, bot_msg = chat
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": bot_msg})

    # 2. BÚSQUEDA TAVILY (Para el precio real de $70k)
    search_context = ""
    if any(p in message.lower() for p in ["precio", "bitcoin", "valor", "noticias", "clima"]):
        try:
            # Buscamos la info más reciente
            search = tavily.search(query=f"{message} hoy {ahora}", search_depth="basic", max_results=1)
            if search and "results" in search and len(search["results"]) > 0:
                # Extraemos el contenido del primer resultado real
                info_fresca = search["results"][0].get("content", "")
                search_context = f"\n\n[DATOS DE RED ACTUALIZADOS]: {info_fresca}"
        except Exception:
            search_context = "\n\n[SISTEMA: Error al conectar con los servidores de datos]"

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        # 3. Generación con el modelo 120B
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=messages,
            temperature=0.7,
            stream=True 
        )
        
        texto_acumulado = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                texto_acumulado += chunk.choices[0].delta.content
                yield texto_acumulado
                
    except Exception as e:
        yield f"Jorge, detecto un inconveniente en el proceso: {str(e)}"

# Interfaz limpia
demo = gr.ChatInterface(fn=adia_chat, title="ADIA")

if __name__ == "__main__":
    # Render asigna el puerto automáticamente
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
