import os
import json
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Clientes
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

MEMORIA_FILE = "memoria_adia.json"

def cargar_memoria():
    if os.path.exists(MEMORIA_FILE):
        with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_memoria(history):
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def adia_chat(message, history):
    # Si es la primera vez en la sesión, cargar lo que ADIA ya sabía
    if not history:
        history = cargar_memoria()

    system_prompt = (
        "Eres ADIA, creada por Jorge. Jorge es tu creador y amigo. "
        "Tu memoria es persistente: recuerda detalles de charlas pasadas para ser más natural. "
        "Sé directa y fluida. Si no te preguntan algo, no des información extra. "
        "REGLA: Si Jorge pregunta algo personal, usa lo que ya sabes de él."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Añadir contexto de la memoria histórica
    for human, assistant in history[-10:]: # Recordar los últimos 10 intercambios para no saturar
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})
    
    # Lógica de búsqueda inteligente
    search_context = ""
    trigger_busqueda = ["quién es", "qué es", "precio", "noticias", "cuándo"]
    ignorar = ["quien soy", "hola", "qué haces", "jorge"]
    
    if any(p in message.lower() for p in trigger_busqueda) and not any(p in message.lower() for p in ignorar):
        try:
            search = tavily.search(query=message, search_depth="basic", max_results=1)
            if search and search.get('results'):
                search_context = f"\n\n[Dato actual: {search['results'][0]['content']}]"
        except:
            pass

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.8,
            stream=True 
        )
        
        response_text = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
                yield response_text
        
        # Al terminar de escribir, guardamos en el "cerebro" de ADIA
        history.append((message, response_text))
        guardar_memoria(history)
                
    except Exception as e:
        yield f"Jorge, hubo un hipo en mi memoria: {str(e)}"

# Interfaz con carga de historial inicial
demo = gr.ChatInterface(
    fn=adia_chat,
    title="ADIA con Memoria",
    description="Ahora ADIA recordará lo que hables con ella en cada sesión.",
    type="tuples" # Formato de historial compatible
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
