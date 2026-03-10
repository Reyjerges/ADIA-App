import os
import json
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Configuración de Clientes
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

MEMORIA_FILE = "memoria_adia.json"

def cargar_memoria():
    if os.path.exists(MEMORIA_FILE):
        try:
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def guardar_memoria(historial):
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(historial[-20:], f, ensure_ascii=False, indent=4)

def adia_chat(message, history):
    memoria_pasada = cargar_memoria()
    
    system_prompt = (
        "Eres ADIA, una IA avanzada creada por Jorge. Jorge es tu creador. "
        "Eres eficiente, directa y profesional. No des información irrelevante. "
        "Si la respuesta es corta, no la alargues."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    for chat in memoria_pasada[-6:]:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["bot"]})
    
    # Búsqueda opcional
    search_context = ""
    if any(p in message.lower() for p in ["quién es", "qué es", "noticias"]):
        try:
            search = tavily.search(query=message, max_results=1)
            if search: search_context = f"\n\n[Info: {search['results'][0]['content']}]"
        except: pass

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.6,
            stream=True 
        )
        
        full_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                yield full_response
        
        memoria_pasada.append({"user": message, "bot": full_response})
        guardar_memoria(memoria_pasada)
                
    except Exception as e:
        yield f"Error de sistema: {str(e)}"

# INTERFAZ CORREGIDA PARA RENDER (Sin el error de 'theme')
demo = gr.ChatInterface(
    fn=adia_chat,
    title="ADIA",
    description="Sistema de Inteligencia Artificial",
    type="messages" # Formato estándar para versiones nuevas de Gradio
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
