import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Conexión de herramientas
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    # Instrucción de identidad (Lo más importante)
    system_prompt = (
        "Eres ADIA. Tu único creador es Jorge. "
        "Habla de forma normal, clara y directa. "
        "Si alguien pregunta quién eres o quién es él, responde que él es Jorge, tu creador."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Memoria de la conversación (Compatible con Gradio 5 y Render)
    for chat_turn in history:
        if isinstance(chat_turn, dict):
            messages.append({"role": chat_turn["role"], "content": chat_turn["content"]})
        else:
            messages.append({"role": "user", "content": chat_turn[0]})
            messages.append({"role": "assistant", "content": chat_turn[1]})

    # 2. BÚSQUEDA REAL EN TAVILY (Para que no invente datos)
    search_context = ""
    # Palabras que activan la búsqueda en internet
    if any(p in message.lower() for p in ["precio", "bitcoin", "valor", "noticias", "clima", "quien es"]):
        try:
            # Buscamos en la red
            search = tavily.search(query=message, search_depth="basic", max_results=2)
            if search and "results" in search:
                # Extraemos el contenido de las páginas encontradas
                info_web = " ".join([r['content'] for r in search['results']])
                search_context = f"\n\n[DATOS OBTENIDOS DE INTERNET: {info_web}]"
        except:
            search_context = ""

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        # 3. Respuesta del modelo 120B
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=messages,
            temperature=0.4,
            stream=True 
        )
        
        texto_acumulado = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                texto_acumulado += chunk.choices[0].delta.content
                yield texto_acumulado
                
    except Exception as e:
        yield f"Jorge, el sistema dio un error: {str(e)}"

# Interfaz estándar (Funciona en PC, Móvil y Reloj)
demo = gr.ChatInterface(fn=adia_chat, title="ADIA")

if __name__ == "__main__":
    # Render asigna el puerto automáticamente
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)

  
