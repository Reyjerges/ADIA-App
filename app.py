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
    palabras_chat = ["hola", "que tal", "como estas", "quien eres", "ok", "gracias", "adios"]
    if consulta.lower().strip() in palabras_chat or len(consulta) < 5:
        return ""
    try:
        contexto = tavily.get_search_context(query=consulta, search_depth="basic", max_results=3)
        return contexto
    except:
        return ""

def responder_adia(mensaje, historial):
    if not api_key:
        return "Jorge, falta la GROQ_API_KEY en Render."

    info_google = buscar_en_internet(mensaje)

    system_prompt = (
        "Eres ADIA, la compañera inteligente de Jorge. "
        f"Contexto: {info_google}. "
        "Eres experta en Godot y programación. Amable, técnica y llamas a Jorge por su nombre."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # Memoria para versiones antiguas de Gradio
    for h in historial:
        mensajes_api.append({"role": "user", "content": h[0]})
        mensajes_api.append({"role": "assistant", "content": h[1]})

    mensajes_api.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_api,
            temperature=0.6
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Jorge, hubo un lío técnico: {str(e)}"

# --- INTERFAZ SIMPLIFICADA (Para evitar errores de versión) ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA")
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    # Render usa el puerto 10000 por defecto si no detecta el otro
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
