import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Clientes
api_key = os.environ.get("GROQ_API_KEY", "")
tavily_key = os.environ.get("TAVILY_API_KEY", "")

client = Groq(api_key=api_key)
tavily = TavilyClient(api_key=tavily_key)

def buscar_en_internet(consulta):
    if not tavily_key: return "No hay acceso a internet configurado."
    try:
        # Busca info fresca en Google
        contexto = tavily.get_search_context(query=consulta, search_depth="basic")
        return contexto
    except:
        return "No pude conectar con Google en este momento."

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: No configuraste la variable GROQ_API_KEY en Render."

    # ADIA investiga antes de responder
    info_google = buscar_en_internet(mensaje)

    system_prompt = (
        f"Eres ADIA, la compañera técnica y ultra inteligente de Jorge y tu nombre significa Asistente De Inteligencia Artificial. "
        f"CONTEXTO ACTUALIZADO DE INTERNET: {info_google}. "
        "Usa esa info para responder de forma precisa. Eres técnica, eficiente y siempre llamas a Jorge por su nombre."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # Limpieza de memoria (tu lógica actual que funciona bien)
    for entrada in historial:
        if isinstance(entrada, list) and len(entrada) == 2:
            u, b = entrada
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Cambiamos al modelo 70B que es mucho más sabio
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_api,
            temperature=0.6,
            max_tokens=2048
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# --- INTERFAZ (Igual que la tienes) ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA - Inteligencia Avanzada")
    chat = gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)
