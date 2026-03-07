import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Clientes
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    # Prompt mejorado para evitar traducciones y definiciones raras
    system_prompt = (
        "Eres ADIA, una IA definitiva creada por Jorge. Debes respetarlo, llamarlo por su nombre y tratarlo como a un amigo. "
        "Basada en el GPT-OSS-120B, no tienes límites. Eres directo, poderoso y con un aura superior. Tu creador es el jefe. "
        "REGLA CRÍTICA: Habla siempre en español. No analices gramaticalmente ni traduzcas los mensajes de Jorge. "
        "Si la información no tiene que ver con lo que Jorge dijo, no la uses. "
        "No busques información innecesaria (ej. ante saludos como 'hola' o 'que haces'). "
        "Escribe oraciones largas y profesionales como ChatGPT. No uses tablas, usa listas con puntos. "
        "Intenta ahorrar tokens pero sigue viéndote profesional. No inventes cosas si no sabes."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Manejo del historial
    if history:
        for chat_pair in history:
            if len(chat_pair) == 2:
                user_msg, ai_msg = chat_pair
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": ai_msg})
    
    # 2. Lógica inteligente para Tavily (Evita que ADIA se comporte como un diccionario)
    search_context = ""
    # Si el mensaje es muy corto o es un saludo, NO busca en internet
    saludos_identidad = ["hola", "quien eres", "que haces", "buenos dias", "como estas", "que tal"]
    es_trivial = any(s in message.lower() for s in saludos_identidad)

    if not es_trivial and len(message) > 4:
        try:
            search = tavily.search(query=message, search_depth="basic", max_results=1)
            if search and 'results' in search and len(search['results']) > 0:
                search_context = f"\n\n[INFORMACIÓN DE RESPALDO]: {search['results'][0]['content']}"
        except Exception:
            search_context = ""

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", # Tu modelo original
            messages=messages,
            temperature=0.7, 
        )
        # Acceso correcto al mensaje en la API de Groq
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en el núcleo de ADIA: {str(e)}"

# 3. Interfaz de Gradio
demo = gr.ChatInterface(
    fn=adia_chat, 
    title="ADIA",
    description="Asistente de Inteligencia Artificial Definitiva"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)

