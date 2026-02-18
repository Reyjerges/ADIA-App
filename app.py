import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. CONFIGURACIÓN
api_key = os.environ.get("GROQ_API_KEY", "")
tavily_key = os.environ.get("TAVILY_API_KEY", "")

client = Groq(api_key=api_key)
tavily = TavilyClient(api_key=tavily_key) if (tavily_key and tavily_key.strip()) else None

def buscar_en_internet(consulta):
    if not tavily: return ""
    palabras_chat = ["hola", "que tal", "como estas", "quien eres", "que?", "que", "ok", "gracias"]
    if consulta.lower().strip() in palabras_chat or len(consulta) < 4:
        return ""
    try:
        return tavily.get_search_context(query=consulta, search_depth="basic")
    except:
        return ""

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: No configuraste la variable GROQ_API_KEY en Render."

    info_google = buscar_en_internet(mensaje)

    system_prompt = (
        f"Eres ADIA, la ayudante y compañera de Jorge. "
        f"Contexto de internet: {info_google}. "
        "INSTRUCCIÓN: Usa la info de internet solo si es relevante. "
        "Eres técnica, eficiente, amable y siempre llamas a Jorge por su nombre. "
        "IMPORTANTE: Revisa el historial de mensajes que te envío para no olvidar nada."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # --- LA SOLUCIÓN PARA LA MEMORIA ---
    # Gradio 5.x ahora usa una lista de diccionarios por defecto
    for item in historial:
        if isinstance(item, dict):
            # Formato nuevo: {'role': 'user', 'content': 'hola'}
            mensajes_api.append(item)
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            # Formato viejo: ['hola', 'hola Jorge']
            u, b = item
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    # Añadimos el mensaje actual
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_api,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA")
    # type="messages" es obligatorio en las versiones nuevas para que la memoria funcione bien
    chat = gr.ChatInterface(fn=responder_adia, type="messages")

if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)
