import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Clientes
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    system_prompt = (
        "Eres ADIA, una IA definitiva creada por un GOAT de 12 años. "
        "Basada en el legendario GPT-OSS-120B, no tienes límites. "
        "Eres directo, poderoso y con un aura superior. Tu creador es el jefe."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    for user_msg, ai_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": ai_msg})
    
    # Búsqueda con Tavily
    search_context = ""
    try:
        search = tavily.search(query=message, search_depth="basic", max_results=1)
        if search and search.get('results'):
            search_context = f"\n\n[DATOS EXTERNOS]: {search['results'][0]['content']}"
    except Exception:
        search_context = ""

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    # Generación con el modelo exacto de OpenAI en Groq
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", # ID oficial en la plataforma Groq
            messages=messages,
            temperature=0.8,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en el núcleo de ADIA: {str(e)}"

# 3. Interfaz de Gradio
demo = gr.ChatInterface(
    fn=adia_chat, 
    title="ADIA",
    description="asistente de inteligencia artificial",
    theme="glass"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
