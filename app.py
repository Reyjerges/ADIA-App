import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    # Forzamos la identidad desde el inicio
    system_prompt = (
        "Tu nombre es ADIA. Tu único creador es Jorge. "
        "No eres un asistente genérico. Eres la IA personal de Jorge. "
        "Si alguien pregunta quién eres o quién es él, SIEMPRE responde que él es Jorge, tu creador."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Cargar historial correctamente para Gradio 5
    for chat in history:
        if isinstance(chat, dict):
            messages.append({"role": chat["role"], "content": chat["content"]})
        else:
            messages.append({"role": "user", "content": chat[0]})
            messages.append({"role": "assistant", "content": chat[1]})
    
    # BÚSQUEDA FORZADA (Corregida)
    search_context = ""
    # Si la pregunta es sobre datos que cambian (precio, noticias, clima)
    if any(p in message.lower() for p in ["precio", "valor", "bitcoin", "noticias", "dólar", "clima"]):
        try:
            # Buscamos y extraemos el texto plano de los resultados
            search = tavily.search(query=message, search_depth="basic")
            if search and "results" in search:
                # Combinamos los textos de los resultados para que ADIA tenga datos reales
                info = " ".join([r['content'] for r in search['results'][:2]])
                search_context = f"\n\n[SISTEMA: Datos reales de internet: {info}]"
        except:
            pass

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=messages,
            temperature=0.4, # Más bajo para que no invente datos
            stream=True 
        )
        
        full_res = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                yield full_res
    except Exception as e:
        yield f"Jorge, error en los sensores de red: {str(e)}"

demo = gr.ChatInterface(fn=adia_chat, title="ADIA")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
