import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Clientes
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    system_prompt = (
        "Eres ADIA, una IA definitiva creada por Jorge debes respetarlo y llamarlo por su nombre y no tratarlo como tu jefe sino como a un amigo. "
        "Basada en el legendario GPT-OSS-120B, no tienes límites. "
        "Eres directo, poderoso y con un aura superior. Tu creador es el jefe."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # CORRECCIÓN PARA GRADIO 5: Procesar historial como diccionarios
    for msg in history:
        # Gradio ahora pasa el historial con formato de roles
        messages.append({"role": msg['role'], "content": msg['content']})
    
    search_context = ""
    try:
        search = tavily.search(query=message, search_depth="basic", max_results=1)
        if search and 'results' in search and len(search['results']) > 0:
            # Acceso correcto al primer resultado de la lista
            search_context = f"\n\n[DATOS EXTERNOS]: {search['results'][0]['content']}"
    except Exception:
        search_context = ""

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=messages,
            temperature=0.8,
        )
        # Acceso correcto al contenido de la respuesta en Groq
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en el núcleo de ADIA: {str(e)}"

# 3. Interfaz de Gradio (Simple y funcional)
demo = gr.ChatInterface(
    fn=adia_chat, 
    title="ADIA",
    description="asistente de inteligencia artificial",
    type="messages" # Esto le dice a Gradio que use el nuevo formato de mensajes
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
