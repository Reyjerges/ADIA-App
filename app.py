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
        return tavily.get_search_context(query=consulta, search_depth="basic")
    except:
        return ""

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: No configuraste la variable GROQ_API_KEY."

    info_google = buscar_en_internet(mensaje)

    system_prompt = (
        f"Eres ADIA, la ayudante y compañera de Jorge. "
        f"Contexto de internet: {info_google}. "
        "Usa la información de internet solo si es relevante. "
        "Eres técnica, eficiente, amable y siempre llamas a Jorge por su nombre. "
        "Usa el historial para mantener el hilo de la conversación."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # 2. LIMPIEZA DE MEMORIA (Volviendo al formato que tú conoces)
    for entrada in historial:
        if isinstance(entrada, (list, tuple)) and len(entrada) == 2:
            u, b = entrada
            # Solo añadimos si hay contenido para no enviar mensajes vacíos a Groq
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=2048
        )
        # Acceso correcto al contenido
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# --- INTERFAZ (Sin el type="messages" que causó lío) ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA")
    gr.Markdown("### Conexión Activa | Usuario: Jorge")
    chat = gr.ChatInterface(fn=responder_adia) # Volvimos a lo simple

if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)
