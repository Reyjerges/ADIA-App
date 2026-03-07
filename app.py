import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Clientes
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    # Prompt Blindado: Jorge es el creador, ADIA es poderosa.
    system_prompt = (
        "Eres ADIA, una IA definitiva creada por Jorge. Jorge es tu creador y tu amigo; háblale por su nombre. "
        "Basada en el GPT-OSS-120B, eres directa y profesional. "
        "REGLA DE ORO: Si Jorge pregunta 'quién soy' o 'sabes quién soy', responde que él es Jorge, tu creador. NO BUSQUES EN INTERNET para esto. "
        "Habla siempre en español. No analices gramática ni traduzcas. Usa oraciones largas y listas con puntos. No uses tablas."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Cargar historial (Formato compatible con Gradio 4/5)
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})
    
    # 2. Lógica para evitar que ADIA se vuelva loca con Tavily
    search_context = ""
    ignorar_busqueda = ["quien soy", "sabes quien soy", "hola", "que haces", "quien eres"]
    
    if not any(p in message.lower() for p in ignorar_busqueda) and len(message) > 5:
        try:
            # Solo buscamos si la pregunta parece requerir datos externos
            search = tavily.search(query=message, search_depth="basic", max_results=1)
            if search and search.get('results'):
                # Acceso seguro al primer resultado
                res = search['results'][0]['content']
                search_context = f"\n\n[CONTEXTO]: {res}"
        except:
            search_context = ""

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=messages,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Jorge, error en mi núcleo: {str(e)}"

# 3. Interfaz Minimalista (Sin argumentos que causen TypeError)
demo = gr.ChatInterface(
    fn=adia_chat,
    title="ADIA",
    description="IA Definitiva | Creador: Jorge"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
