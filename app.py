import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. LLAVES
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
        return "Error: No configuraste GROQ_API_KEY."

    info_google = buscar_en_internet(mensaje)

    system_prompt = (
        f"Eres ADIA, la compañera de Jorge. Contexto: {info_google}. "
        "Usa el historial para recordar lo que hablaron. Sé técnica y amable. "
        "Siempre llama a Jorge por su nombre."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # 2. MEMORIA MANUAL (Funciona en todas las versiones de Gradio)
    for entrada in historial:
        # Si Gradio envía el historial como [usuario, bot]
        if isinstance(entrada, (list, tuple)) and len(entrada) == 2:
            u, b = entrada
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})
        # Si Gradio envía el historial como {'role': '...', 'content': '...'}
        elif isinstance(entrada, dict):
            mensajes_api.append(entrada)

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

# --- INTERFAZ SIN 'TYPE' ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA")
    # Quitamos el 'type' para que no explote Render
    chat = gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)
