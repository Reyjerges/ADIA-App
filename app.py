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
        except:
            return []
    return []

def guardar_memoria(historial):
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(historial[-20:], f, ensure_ascii=False, indent=4)

def adia_chat(message, history):
    memoria_pasada = cargar_memoria()
    
    # Prompt de ADIA: Identidad única y directa
    system_prompt = (
        "Eres ADIA, una inteligencia artificial avanzada creada por Jorge. "
        "Jorge es tu creador. Tu trato hacia él es de respeto y eficiencia. "
        "Tu objetivo es ser útil y responder de forma natural y fluida. "
        "REGLA CRÍTICA: No entregues información que no sea relevante para la consulta. "
        "Si la respuesta es breve, mantenla breve. Evita introducciones innecesarias."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Contexto de memoria para continuidad
    for chat in memoria_pasada[-6:]:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["bot"]})
    
    # Búsqueda externa solo si es necesario
    search_context = ""
    trigger_busqueda = ["quién es", "qué es", "noticias", "precio", "cuándo"]
    ignorar = ["quien soy", "hola", "jorge", "adia"]
    
    if any(p in message.lower() for p in trigger_busqueda) and not any(p in message.lower() for p in ignorar):
        try:
            search = tavily.search(query=message, search_depth="basic", max_results=1)
            if search and search.get('results'):
                search_context = f"\n\n[Dato externo: {search['results'][0]['content']}]"
        except:
            pass

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        # Generación con Streaming (Palabra por palabra)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.6,
            stream=True 
        )
        
        full_response = ""
        for chunk in completion:
            if chunk.choices.delta.content:
                full_response += chunk.choices.delta.content
                yield full_response
        
        # Guardar interacción
        memoria_pasada.append({"user": message, "bot": full_response})
        guardar_memoria(memoria_pasada)
                
    except Exception as e:
        yield f"Jorge, he encontrado un inconveniente técnico: {str(e)}"

# Interfaz Gradio
demo = gr.ChatInterface(
    fn=adia_chat,
    title="ADIA",
    description="Sistema de Inteligencia Artificial",
    theme="default"
)

if __name__ == "__main__":
    # Configuración de puerto para Render
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port, share=False)
