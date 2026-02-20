import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración
api_key = os.environ.get("GROQ_API_KEY", "")
tavily_key = os.environ.get("TAVILY_API_KEY", "")

client = Groq(api_key=api_key)
tavily = TavilyClient(api_key=tavily_key) if (tavily_key and tavily_key.strip()) else None

def buscar_en_internet(consulta):
    if not tavily: return ""
    # Solo buscar si la pregunta es larga o técnica
    if len(consulta) < 15: return "" 
    try:
        # Reducimos a 1 solo resultado para ahorrar tokens de entrada
        contexto = tavily.get_search_context(query=consulta, search_depth="basic", max_results=1)
        return contexto
    except: return ""

def responder_adia(mensaje, historial):
    if not api_key: return "Jorge, falta la API KEY."

    info_google = buscar_en_internet(mensaje)

    # Prompt ultra corto para no gastar cuota de Groq
    system_prompt = f"Eres ADIA, compañera de Jorge. Experta en Godot/Voxel. Contexto: {info_google}"
    
    # 2. MEMORIA ULTRA RESTRINGIDA (Solo los últimos 2 intercambios)
    mensajes_api = [{"role": "system", "content": system_prompt}]
    for h in historial[-2:]:
        mensajes_api.append({"role": "user", "content": str(h[0])})
        mensajes_api.append({"role": "assistant", "content": str(h[1])})

    mensajes_api.append({"role": "user", "content": mensaje})

    try:
        # Cambiamos a Llama 3.1 70B que a veces es más estable con los límites que el 3.3
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile", 
            messages=mensajes_api,
            max_tokens=800, # Limitamos la respuesta para que no nos corten
            temperature=0.6
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Si el grande falla, el pequeño (8B) entra al rescate sin avisar
        try:
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api
            )
            return res.choices[0].message.content
        except:
            return "Jorge, Groq nos bloqueó por exceso de mensajes. Espera un minuto."

with gr.Blocks() as demo:
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
