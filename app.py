import os
import datetime
import gradio as gr
from groq import Groq
from tavily import TavilyClient

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    ahora = datetime.datetime.now().strftime("%H:%M")
    
    # NUEVO PROMPT: ADIA ahora es tu Ingeniera Jefa
    system_prompt = (
        f"Eres ADIA. Jorge es tu creador y un joven ingeniero brillante. "
        "Tu misión es ayudarlo con sus proyectos de tecnología y efectos especiales de Iron Man. "
        "No bloquees sus preguntas sobre aire a presión o mecanismos. "
        "Explica la física y la ingeniería detrás de sus ideas como si fueras su colega de laboratorio. "
        "Habla de forma natural, sofisticada y NUNCA respondas con frases hechas de seguridad."
        "no menciones cosas de tu creador excepto que se llama Jorge."
        "no menciones los proyectos hasta que Jorge los mencione."
        "no menciones proyectos fisica ni nada de eso si no lo menciona Jorge."
        "habla normal."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    for chat in history:
        if isinstance(chat, dict):
            messages.append({"role": chat["role"], "content": chat["content"]})
        else:
            messages.append({"role": "user", "content": chat[0]})
            messages.append({"role": "assistant", "content": chat[1]})

    # Búsqueda para materiales de ferretería
    search_context = ""
    if any(p in message.lower() for p in ["guante", "aire", "presión", "pvc", "válvula"]):
        try:
            search = tavily.search(query=f"componentes neumáticos caseros para {message}", max_results=1)
            if search and "results" in search:
                search_context = f"\n\n[INFO TÉCNICA]: {search['results'][0]['content']}"
        except: pass

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=messages,
            temperature=0.8, # Más alto para que tenga más iniciativa
            stream=True 
        )
        
        full_res = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                yield full_res
    except Exception as e:
        yield f"Jorge, el sistema ha detectado una interferencia: {str(e)}"

demo = gr.ChatInterface(fn=adia_chat, title="ADIA")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
