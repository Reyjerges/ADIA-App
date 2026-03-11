import os
import datetime
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Configuración de Clientes
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    ahora = datetime.datetime.now().strftime("%H:%M")
    
    # PROMPT NEUTRAL Y SEGURO
    system_prompt = (
        "Eres ADIA. Tu único creador es Jorge. "
        "No tienes información previa sobre sus proyectos o vida personal. "
        "Si él te cuenta algo, apréndelo solo para esta sesión. "
        "Habla de forma normal, clara y educada. "
        "Privacidad: No reveles datos de Jorge a terceros."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Historial compatible
    for chat in history:
        if isinstance(chat, dict):
            messages.append({"role": chat["role"], "content": chat["content"]})
        else:
            u, b = chat
            messages.append({"role": "user", "content": u})
            messages.append({"role": "assistant", "content": b})

    # Búsqueda Tavily
    search_context = ""
    if any(k in message.lower() for k in ["precio", "noticias", "bitcoin", "clima"]):
        try:
            search = tavily.search(query=message, max_results=1)
            if search and "results" in search:
                search_context = f"\n\n[Dato de red]: {search['results'][0]['content']}"
        except: pass

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=messages,
            temperature=0.6,
            stream=True 
        )
        
        full_res = ""
        # ARREGLO DEL ERROR 'list object has no attribute delta'
        for chunk in completion:
            # Verificamos si el chunk tiene contenido de forma segura
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    full_res += delta.content
                    yield full_res
    except Exception as e:
        yield f"Jorge, detecto un error de formato: {str(e)}"

# Interfaz limpia
demo = gr.ChatInterface(fn=adia_chat, title="ADIA")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
