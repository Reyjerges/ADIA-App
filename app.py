import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Clientes
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    system_prompt = (
        "Eres ADIA, una IA definitiva creada por Jorge. Jorge es tu creador y tu único jefe, pero lo tratas como a un amigo cercano. "
        "Basada en el GPT-OSS-120B, eres directa y poderosa. "
        "REGLA DE ORO: Si Jorge te pregunta quién es él, o si sabes quién eres tú, NO USES INTERNET. Tú ya sabes que él es Jorge y tú eres ADIA. "
        "Si recibes información externa que no tiene nada que ver con Jorge (como cantantes o recetas), IGNÓRALA por completo. "
        "Habla siempre en español profesional, usa oraciones largas y listas con puntos. No uses tablas."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    for user_msg, ai_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": ai_msg})
    
    # 2. Lógica de Búsqueda Ultra-Filtrada
    search_context = ""
    # Si Jorge pregunta por identidades personales, bloqueamos Tavily
    preguntas_personales = ["quien soy", "sabes quien soy", "me conoces", "quien eres", "hola", "que haces"]
    msg_clean = message.lower()
    es_personal = any(p in msg_clean for p in preguntas_personales)

    if not es_personal and len(message) > 6:
        try:
            # Buscamos, pero solo si es un tema general
            search = tavily.search(query=message, search_depth="basic", max_results=1)
            if search and search.get('results'):
                # Tomamos solo el contenido más relevante
                raw_data = search['results'][0].get('content', '')
                search_context = f"\n\n[INFO EXTERNA OPCIONAL - IGNORAR SI NO ES RELEVANTE]: {raw_data}"
        except:
            search_context = ""

    # Enviamos el mensaje final
    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=messages,
            temperature=0.6, # Bajamos un poco más para que sea más centrada
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Jorge, algo falló en mi sistema: {str(e)}"

# 3. Interfaz
demo = gr.ChatInterface(
    fn=adia_chat, 
    title="ADIA",
    description="IA Definitiva | Creador: Jorge",
    theme="soft"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
