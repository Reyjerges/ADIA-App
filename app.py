import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Clientes
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
        contexto = tavily.get_search_context(query=consulta, search_depth="basic")
        return contexto
    except:
        return ""

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: No configuraste la variable GROQ_API_KEY en Render."

    # ADIA investiga en Google
    info_google = buscar_en_internet(mensaje)

    system_prompt = (
        f"Eres ADIA, la compañera de Jorge. Contexto de internet: {info_google}. "
        "Eres técnica, eficiente, amable y siempre llamas a Jorge por su nombre. "
        "Usa el historial para mantener el hilo de la conversación y no olvidar nada."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # 2. MEMORIA CORREGIDA (Extracción de texto puro)
    for entrada in historial:
        if isinstance(entrada, (list, tuple)) and len(entrada) == 2:
            u, b = entrada
            # Si vienen como diccionarios {'text': '...'}, sacamos solo el texto
            if isinstance(u, dict): u = u.get("text", str(u))
            if isinstance(b, dict): b = b.get("text", str(b))
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})
        elif isinstance(entrada, dict):
            rol = entrada.get("role")
            cont = entrada.get("content")
            if isinstance(cont, dict): cont = cont.get("text", str(cont))
            if rol and cont:
                mensajes_api.append({"role": rol, "content": str(cont)})

    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Usamos el modelo 8B para que funcione YA mismo sin bloqueos
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=2048
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA")
    chat = gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)
