import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Clientes
api_key = os.environ.get("GROQ_API_KEY", "")
tavily_key = os.environ.get("TAVILY_API_KEY", "")

client = Groq(api_key=api_key)
tavily = TavilyClient(api_key=tavily_key) if (tavily_key and tavily_key.strip()) else None

def buscar_web(consulta):
    """Busca en internet si la pregunta es técnica o de actualidad."""
    if not tavily or len(consulta) < 8: return ""
    try:
        # Traemos contexto real de la web
        return tavily.get_search_context(query=consulta, search_depth="basic", max_results=2)
    except: return ""

def responder_adia(mensaje, historial):
    if not api_key: return "Jorge, falta la API KEY en Render."

    # Buscamos información en tiempo real
    contexto_web = buscar_web(mensaje)

    # Identidad técnica y seria
    system_prompt = (
        f"Eres ADIA, la compañera técnica de Jorge. Contexto web: {contexto_web}. "
        "Eres directa, eficiente y NUNCA usas palabras cariñosas. "
        "Llama a Jorge por su nombre. RECUERDA: Tienes memoria de los mensajes anteriores."
    )
    
    # 2. CONSTRUCCIÓN DE MEMORIA MANUAL (Universal para Gradio)
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # El historial en versiones viejas es una lista de listas [[user, bot], [user, bot]]
    for h in historial:
        if h[0]: mensajes_api.append({"role": "user", "content": str(h[0])})
        if h[1]: mensajes_api.append({"role": "assistant", "content": str(h[1])})

    # Añadimos el mensaje actual de Jorge
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Usamos Llama 3.3 70B para máxima inteligencia
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_api,
            temperature=0.5,
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Respaldo al modelo rápido si el grande falla
        try:
            backup = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api
            )
            return backup.choices[0].message.content
        except:
            return f"Jorge, error de conexión: {str(e)}"

# --- INTERFAZ COMPATIBLE ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA")
    # Sin el parámetro 'type' para evitar el error de Render
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=port)
