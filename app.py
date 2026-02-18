import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración del Cliente
api_key = os.environ.get("GROQ_API_KEY", "")
tavily_key = os.environ.get("TAVILY_API_KEY", "")

client = Groq(api_key=api_key)
tavily = TavilyClient(api_key=tavily_key) if (tavily_key and tavily_key.strip()) else None

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: No configuraste la variable GROQ_API_KEY en Render."

    # --- LÓGICA DE MEMORIA Y LIMPIEZA ---
    system_prompt = (
        "Eres ADIA, la ayudante y compañera de Jorge. "
        "Eres técnica, eficiente y siempre llamas a Jorge por su nombre."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # Limpiamos el historial para que ADIA entienda solo el texto
    for entrada in historial:
        u, b = None, None
        if isinstance(entrada, (list, tuple)) and len(entrada) == 2:
            u, b = entrada
        elif isinstance(entrada, dict):
            u = entrada.get("user")
            b = entrada.get("assistant")
            
        # Si el mensaje viene como {'text': '...'}, extraemos solo el texto
        if isinstance(u, dict): u = u.get("text", str(u))
        if isinstance(b, dict): b = b.get("text", str(b))
        
        if u: mensajes_api.append({"role": "user", "content": str(u)})
        if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_api,
            temperature=0.7
        )
        # EXTRAEMOS SOLO EL CONTENIDO (Texto limpio)
        respuesta = completion.choices[0].message.content
        return respuesta
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA")
    chat = gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)
