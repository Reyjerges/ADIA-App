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
    # Evitar búsquedas innecesarias para ahorrar cuota de Tavily
    palabras_chat = ["hola", "que tal", "como estas", "quien eres", "ok", "gracias", "adios"]
    if consulta.lower().strip() in palabras_chat or len(consulta) < 5:
        return ""
    try:
        # Usamos búsqueda básica para no consumir créditos de más
        contexto = tavily.get_search_context(query=consulta, search_depth="basic", max_results=3)
        return contexto
    except:
        return ""

def responder_adia(mensaje, historial):
    if not api_key:
        return "Jorge, olvidas configurar la GROQ_API_KEY. Sin ella no puedo despertar."

    # ADIA investiga solo si es necesario
    info_google = buscar_en_internet(mensaje)

    # Prompt de sistema optimizado
    system_prompt = (
        "Eres ADIA, la compañera inteligente y técnica de Jorge. "
        f"Contexto actual de internet: {info_google}. "
        "Eres extremadamente eficiente, amable y siempre te diriges a Jorge por su nombre. "
        "Usa el historial para dar respuestas coherentes y profundas."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # 2. MEMORIA OPTIMIZADA (Limitamos a los últimos 6 mensajes para no saturar Groq)
    for entrada in historial[-6:]:
        if isinstance(entrada, (list, tuple)):
            u, b = entrada
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})
        elif isinstance(entrada, dict):
            mensajes_api.append({"role": entrada.get("role"), "content": str(entrada.get("content"))})

    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # CAMBIO DE MODELO: Llama 3.3 70B es mucho más inteligente que el 8B
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_api,
            temperature=0.6, # Un poco más bajo para mayor precisión técnica
            max_tokens=1500  # Suficiente para respuestas largas sin exceder límites
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Si el modelo 70B falla por límites, ADIA intenta con el rápido automáticamente
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api
            )
            return f"(Modo ahorro) {completion.choices[0].message.content}"
        except:
            return f"Lo siento Jorge, Groq está saturado ahora mismo. Error: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA (Powered by Llama 3.3 70B)")
    # ChatInterface maneja el historial automáticamente
    chat = gr.ChatInterface(
        fn=responder_adia,
        title="ADIA",
        description="Compañera técnica avanzada para Jorge.",
        examples=["¿Cuál es el estado actual de la IA?", "Ayúdame con un script de Python", "Jorge necesita un resumen de noticias"],
        type="messages" # Formato moderno de Gradio 5
    )

server_port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=server_port)
