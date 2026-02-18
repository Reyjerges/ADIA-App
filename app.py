import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. CONFIGURACIÓN DE LAS LLAVES (Render)
api_key = os.environ.get("GROQ_API_KEY", "")
tavily_key = os.environ.get("TAVILY_API_KEY", "")

client = Groq(api_key=api_key)
tavily = TavilyClient(api_key=tavily_key) if tavily_key else None

def buscar_en_internet(consulta):
    """Investiga en Google solo si la pregunta es compleja."""
    if not tavily: return ""
    # Filtro para no buscar cosas simples y ahorrar cuota
    palabras_chat = ["hola", "que tal", "como estas", "quien eres", "que?", "que", "ok", "gracias", "adios"]
    if consulta.lower().strip() in palabras_chat or len(consulta) < 4:
        return ""
    try:
        return tavily.get_search_context(query=consulta, search_depth="basic")
    except:
        return ""

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: No configuraste la variable GROQ_API_KEY en Render."

    # ADIA investiga en internet
    info_google = buscar_en_internet(mensaje)

    system_prompt = (
        f"Eres ADIA, la ayudante y compañera de Jorge. "
        f"Contexto de internet: {info_google}. "
        "INSTRUCCIÓN: Usa la info de internet solo si es relevante para la duda de Jorge. "
        "Eres técnica, eficiente, amable y siempre llamas a Jorge por su nombre. "
        "IMPORTANTE: Tienes acceso al historial de esta conversación. Úsalo para no olvidar lo que hablaron antes."
    )
    
    # --- RECONSTRUCCIÓN DE LA MEMORIA (HISTORIAL) ---
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # Procesamos el historial para que ADIA recuerde
    for entrada in historial:
        if isinstance(entrada, (list, tuple)) and len(entrada) == 2:
            u, b = entrada
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    # Añadimos el mensaje actual de Jorge
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Usamos el modelo más inteligente (Llama 3.3 70B)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=2048
        )
        # Extraemos la respuesta limpia
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# --- INTERFAZ LIMPIA ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA")
    gr.Markdown("### Conexión Segura | Usuario: Jorge")
    # No usamos 'type', usamos la configuración estándar que ya conocemos
    chat = gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    # Configuración de puerto para Render
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)
