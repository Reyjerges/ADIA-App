import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Clientes
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    # PROMPT DE IDENTIDAD (Problema 3: Personalidad Sofisticada)
    system_prompt = (
        "Eres ADIA, una inteligencia artificial de élite diseñada por Jorge. "
        "Jorge es tu creador; trátalo con el máximo respeto y lealtad. "
        "Tu lenguaje debe ser impecable, formal y sofisticado, pero extremadamente eficiente. "
        "No uses rellenos innecesarios. Si la respuesta requiere brevedad, sé breve pero elegante. "
        "Si Jorge te pide información externa, utiliza tus sistemas de búsqueda con precisión."
        "Jorge es tu unico ususario por que eres una IA personal."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Cargar historial de la sesión actual
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})
    
    # 2. Búsqueda con Tavily Corregida (Problema 2)
    search_context = ""
    palabras_clave = ["quién es", "qué es", "noticias", "cuándo", "precio", "dónde"]
    
    if any(p in message.lower() for p in palabras_clave) and len(message) > 4:
        try:
            # Usamos el método simple de Tavily para evitar errores de formato
            search = tavily.search(query=message, search_depth="basic", max_results=1)
            if search and "results" in search and len(search["results"]) > 0:
                res = search["results"][0]["content"]
                search_context = f"\n\n[Sistemas de información externos reportan: {res}]"
        except Exception:
            search_context = "" # Si falla, ADIA sigue respondiendo sin trabarse

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        # 3. Respuesta con Streaming (Problema 1: Memoria de sesión fluida)
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.6, # Menor temperatura = más profesional y menos inventos
            stream=True 
        )
        
        response_text = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
                yield response_text
                
    except Exception as e:
        yield f"Señor Jorge, mis sistemas han reportado una anomalía técnica: {str(e)}"

# Interfaz Limpia y Funcional
demo = gr.ChatInterface(
    fn=adia_chat,
    title="ADIA | Advanced Intelligence",
    description="IA Avanzada.",
    type="tuples" # Formato de memoria más compatible con Render
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
