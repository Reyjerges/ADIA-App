import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Clientes (Variables de Entorno en Render)
api_key = os.environ.get("GROQ_API_KEY", "")
tavily_key = os.environ.get("TAVILY_API_KEY", "")

client = Groq(api_key=api_key)
tavily = TavilyClient(api_key=tavily_key) if tavily_key else None

def buscar_en_internet(consulta):
    """Solo busca si hay una llave y el mensaje es relevante."""
    if not tavily: 
        return "Búsqueda no disponible."
    
    # Lista de palabras que NO deben activar Google
    palabras_chat = ["hola", "que tal", "como estas", "quien eres", "que?", "que", "ok", "gracias"]
    if consulta.lower().strip() in palabras_chat or len(consulta) < 4:
        return "Charla casual, no buscar datos."

    try:
        # Busca información limpia y resumida
        contexto = tavily.get_search_context(query=consulta, search_depth="basic")
        return contexto
    except:
        return "Error al buscar en internet."

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: No configuraste la variable GROQ_API_KEY en Render."

    # 2. ADIA decide si investigar o no
    info_google = buscar_en_internet(mensaje)

    # 3. System Prompt Mejorado
    system_prompt = (
        f"Eres ADIA, la compañera técnica de Jorge. "
        f"Contexto de Internet: {info_google}. "
        "INSTRUCCIÓN: Si el contexto de internet no tiene relación con lo que Jorge dice, IGNÓRALO. "
        "Si Jorge solo te saluda o hace charla casual, responde de forma natural, técnica y amable. "
        "Nunca menciones datos de Google si no te los piden. Siempre llama a Jorge por su nombre."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # 4. Limpieza de memoria para Gradio
    for entrada in historial:
        if isinstance(entrada, (list, tuple)) and len(entrada) == 2:
            u, b = entrada
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # 5. Usando el modelo más inteligente (70B)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_api,
            temperature=0.6,
            max_tokens=2048
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA - Inteligencia Artificial")
    chat = gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    # Render usa el puerto de la variable de entorno
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)
