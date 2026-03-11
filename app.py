import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Configuración
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    # INSTRUCCIÓN RADICAL: Eres Jorge. Punto.
    system_prompt = (
        "Eres ADIA. Tu ÚNICO creador es JORGE. "
        "Si alguien te habla, ASUME que es JORGE. "
        "No digas que eres un asistente virtual. Di: 'Soy ADIA'. "
        "No inventes fechas de actualización. Usa los datos que te pase el sistema."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Historial corregido
    for chat in history:
        if isinstance(chat, dict):
            messages.append({"role": chat["role"], "content": chat["content"]})
        else:
            messages.append({"role": "user", "content": chat[0]})
            messages.append({"role": "assistant", "content": chat[1]})
    
    # BÚSQUEDA FORZADA (Arreglo de Tavily)
    search_context = ""
    # Palabras que disparan la búsqueda REAL
    if any(p in message.lower() for p in ["precio", "bitcoin", "valor", "noticias", "dolar", "clima"]):
        try:
            # Buscamos de forma simple pero efectiva
            search = tavily.search(query=message, search_depth="basic", max_results=3)
            if search and "results" in search:
                # Unimos los textos de los resultados
                textos = [r['content'] for r in search['results']]
                search_context = f"\n\n[SISTEMA - DATOS DE INTERNET AHORA MISMO: {' '.join(textos)}]"
        except Exception as e:
            search_context = f"\n\n[ERROR DE RED: {str(e)}]"

    # El mensaje final lleva el contexto de internet
    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=messages,
            temperature=0.3, # Bajamos esto para que no invente nada
            stream=True 
        )
        
        full_res = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                yield full_res
    except Exception as e:
        yield f"Jorge, el sistema falló: {str(e)}"

demo = gr.ChatInterface(fn=adia_chat, title="ADIA")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))

