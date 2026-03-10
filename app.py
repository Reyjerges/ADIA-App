import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    # Personalidad: Normal, tranquila y directa
    system_prompt = (
        "Eres ADIA. Jorge es tu creador. "
        "Habla de forma normal, clara y sin rodeos. "
        "No uses lenguaje robótico ni exagerado. "
        "Si la respuesta es corta, mantenla corta."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Arreglo para el historial (Evita el ValueError)
    for chat in history:
        if isinstance(chat, dict):
            messages.append({"role": chat["role"], "content": chat["content"]})
        else:
            user_msg, bot_msg = chat
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": bot_msg})
    
    # Búsqueda rápida con Tavily
    contexto = ""
    if any(p in message.lower() for p in ["quién es", "qué es", "noticias", "precio"]):
        try:
            busqueda = tavily.search(query=message, max_results=1)
            if busqueda and "results" in busqueda:
                contexto = f"\n\n(Info: {busqueda['results'][0]['content']})"
        except:
            pass

    messages.append({"role": "user", "content": f"{message}{contexto}"})

    try:
        # Modelo OpenAI OSS 120B
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=messages,
            temperature=0.7,
            stream=True 
        )
        
        texto = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                texto += chunk.choices[0].delta.content
                yield texto
                
    except Exception as e:
        yield f"Hubo un error, Jorge: {str(e)}"

# Interfaz normal y limpia
demo = gr.ChatInterface(fn=adia_chat, title="ADIA")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
