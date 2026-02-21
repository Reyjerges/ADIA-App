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
    if not tavily or len(consulta) < 10: return ""
    try:
        # Buscamos solo 2 resultados para no saturar de texto el prompt
        contexto = tavily.get_search_context(query=consulta, search_depth="basic", max_results=2)
        return contexto
    except: return ""

def responder_adia(mensaje, historial):
    if not api_key: return "Jorge, falta la API KEY."

    # 2. Búsqueda inteligente (Solo si Jorge pregunta algo que requiera datos nuevos)
    info_google = buscar_en_internet(mensaje)

    # Identidad técnica y seria (Memoria activada en el sistema)
    system_prompt = (
        f"Eres ADIA, la compañera técnica de Jorge. Contexto de internet: {info_google}. "
        "Tu tono es profesional, directo y eficiente. NUNCA uses palabras cariñosas. "
        "Llama a Jorge por su nombre. TIENES MEMORIA: utiliza el historial para ser coherente."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # 3. MEMORIA REAL: Inyectamos el historial completo (últimos 6 mensajes)
    # Gradio entrega el historial como una lista de listas [[user, bot], ...]
    for h in historial:
        if isinstance(h, (list, tuple)) and len(h) == 2:
            u, b = h
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    # Añadimos el mensaje actual de Jorge
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Llama 3.3 70B para máximo razonamiento
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_api,
            temperature=0.6,
            max_tokens=1200
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Respaldo si el modelo grande falla
        try:
            backup = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api
            )
            return backup.choices[0].message.content
        except:
            return f"Jorge, el sistema se saturó. Error: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA (Memoria y Buscador OK)")
    # 'type="messages"' es clave en versiones nuevas de Gradio para el historial
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=port)
