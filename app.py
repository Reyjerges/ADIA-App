import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Clientes
api_key = os.environ.get("GROQ_API_KEY", "")
tavily_key = os.environ.get("TAVILY_API_KEY", "")

client = Groq(api_key=api_key)
tavily = TavilyClient(api_key=tavily_key) if tavily_key else None

def buscar_en_internet(consulta):
    if not tavily: return ""
    palabras_chat = ["hola", "que tal", "como estas", "quien eres", "que?", "que", "ok", "gracias"]
    if consulta.lower().strip() in palabras_chat or len(consulta) < 4:
        return ""
    try:
        # Busca información actualizada
        return tavily.get_search_context(query=consulta, search_depth="basic")
    except:
        return ""

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: No configuraste la variable GROQ_API_KEY en Render."

    # ADIA investiga si la pregunta lo requiere
    info_google = buscar_en_internet(mensaje)

    # System Prompt: Volvemos a la esencia de ADIA
    system_prompt = (
        f"Eres ADIA, la ayudante y compañera de Jorge. "
        f"Contexto de internet: {info_google}. "
        "Usa la información de internet solo si Jorge pregunta algo de actualidad. "
        "Eres técnica, eficiente, amable y siempre llamas a Jorge por su nombre. "
        "Mantén el hilo de la conversación usando el historial."
    )
    
    # RECONSTRUCCIÓN DE MEMORIA
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # Esto permite que ADIA recuerde lo que hablaron arriba
    for entrada in historial:
        if isinstance(entrada, (list, tuple)) and len(entrada) == 2:
            u, b = entrada
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Usando el modelo 70B para que sea más inteligente
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=2048
        )
        return completion.choices.message.content
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# --- INTERFAZ LIMPIA ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA")
    gr.Markdown("### IA")
    chat = gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)
