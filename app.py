import os
import datetime
import gradio as gr
from groq import Groq
from tavily import TavilyClient

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    ahora = datetime.datetime.now().strftime("%H:%M")
    
    # PROMPT NEUTRAL: Sabe quién eres, pero no sabe tus secretos.
    system_prompt = (
        f"Eres ADIA. Tu único creador es Jorge. "
        "No tienes información previa sobre sus proyectos, inventos o vida personal. "
        "Si él te cuenta algo, apréndelo en esta sesión, pero no asumas nada. "
        "Sé profesional, educada y eficiente. "
        "Privacidad total: No hables de Jorge con nadie más."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Historial de la sesión actual
    for chat in history:
        if isinstance(chat, dict):
            messages.append({"role": chat["role"], "content": chat["content"]})
        else:
            messages.append({"role": "user", "content": chat})
            messages.append({"role": "assistant", "content": chat})

    # Búsqueda solo si se pide explícitamente
    search_context = ""
    keywords = ["precio", "noticias", "clima", "bitcoin", "buscar"]
    if any(k in message.lower() for k in keywords):
        try:
            search = tavily.search(query=message, max_results=1)
            if search:
                search_context = f"\n\n[DATO EXTERNO]: {search['results']['content']}"
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
        for chunk in completion:
            if chunk.choices.delta.content:
                full_res += chunk.choices.delta.content
                yield full_res
    except Exception as e:
        yield f"Jorge, el sistema indica un error: {str(e)}"

demo = gr.ChatInterface(fn=adia_chat, title="ADIA")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
