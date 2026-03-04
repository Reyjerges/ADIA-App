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
        "No te vuelvas loco dando informacion si no tiene nada que ver,ejemplo:si Jorge dice hola contesale sin definicion ni nada raro."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Compatibilidad para Gradio 4.x (donde history es una lista de listas [user, bot])
    if history:
        for chat_pair in history:
            if len(chat_pair) == 2:
                user_msg, ai_msg = chat_pair
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": ai_msg})
    
    search_context = ""
    try:
        search = tavily.search(query=message, search_depth="basic", max_results=1)
        if search and 'results' in search and len(search['results']) > 0:
            # CORRECCIÓN: Acceso al índice [0] de la lista de resultados
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
        # Acceso correcto al contenido en Groq
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en el núcleo de ADIA: {str(e)}"

# 3. Interfaz de Gradio (Versión compatible)
demo = gr.ChatInterface(
    fn=adia_chat, 
    title="ADIA",
    description="asistente de inteligencia artificial"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
