import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    # Identidad forzada para que nunca olvide quién eres
    system_prompt = (
        "Eres ADIA. Tu creador es Jorge. "
        "Habla de forma clara, natural y directa. "
        "Si Jorge pregunta quién es, responde siempre que es Jorge, tu creador."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Manejo de historial compatible con Gradio 5
    for chat in history:
        if isinstance(chat, dict):
            messages.append({"role": chat["role"], "content": chat["content"]})
        else:
            messages.append({"role": "user", "content": chat[0]})
            messages.append({"role": "assistant", "content": chat[1]})
    
    # BUSQUEDA REAL (Corrección de Bitcoin y datos)
    contexto = ""
    # Si la pregunta pide datos actuales, forzamos búsqueda
    if any(p in message.lower() for p in ["precio", "valor", "bitcoin", "noticias", "clima", "quien es"]):
        try:
            busqueda = tavily.search(query=message, search_depth="basic", max_results=1)
            if busqueda and "results" in busqueda and len(busqueda["results"]) > 0:
                # Sacamos el texto real de la web
                info_web = busqueda["results"][0]["content"]
                contexto = f"\n\n(Dato real encontrado: {info_web})"
        except:
            pass

    messages.append({"role": "user", "content": f"{message}{contexto}"})

    try:
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
        yield f"Lo siento Jorge, hubo un error: {str(e)}"

demo = gr.ChatInterface(fn=adia_chat, title="ADIA")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
