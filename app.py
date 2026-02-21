import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Poder
api_key = os.environ.get("GROQ_API_KEY", "")
tavily_key = os.environ.get("TAVILY_API_KEY", "")

client = Groq(api_key=api_key)
tavily = TavilyClient(api_key=tavily_key) if (tavily_key and tavily_key.strip()) else None

def buscar_en_internet(consulta):
    """Busca en Google usando Tavily."""
    if not tavily or len(consulta) < 8: return ""
    try:
        # Traemos contexto real de la web para ADIA
        return tavily.get_search_context(query=consulta, search_depth="basic", max_results=2)
    except: return ""

def responder_adia(mensaje, historial):
    """Función de chat con memoria manual para Render."""
    if not api_key: return "Jorge, falta la API KEY en Render."

    # ADIA investiga en tiempo real
    contexto_web = buscar_en_internet(mensaje)

    # Identidad técnica y directa
    system_prompt = (
        f"Eres ADIA, la compañera de Jorge. Contexto internet: {contexto_web}. "
        "Eres técnica, seria y directa. NUNCA uses palabras cariñosas. "
        "Llama a Jorge por su nombre. RECUERDA: Tienes memoria de lo hablado antes."
    )
    
    # 2. CONSTRUCCIÓN DE MEMORIA MANUAL (Universal para Gradio)
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # Recorremos el historial para que ADIA no olvide nada
    for h in historial:
        # En versiones viejas el historial es [usuario, bot]
        if isinstance(h, (list, tuple)):
            mensajes_api.append({"role": "user", "content": str(h[0])})
            mensajes_api.append({"role": "assistant", "content": str(h[1])})

    # Añadimos el mensaje actual
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Usamos Llama 3.3 70B para máxima inteligencia
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_api,
            temperature=0.5,
            max_tokens=1000
        )
        # Acceso directo al contenido de la respuesta
        return completion.choices[0].message.content
    except Exception as e:
        # Respaldo si el 70B se satura
        try:
            backup = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api
            )
            return backup.choices[0].message.content
        except:
            return f"Jorge, el sistema se saturó: {str(e)}"

# --- INTERFAZ SIN 'TYPE' (Nativo Render) ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA")
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    # Render usa el puerto 10000 por defecto
    port = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=port)
