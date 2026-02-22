import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Conexión con las APIs
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_logic(mensaje, historial):
    # 1. Identidad Reforzada
    mensajes_ia = [
        {"role": "system", "content": "Eres ADIA, una IA experta en Anime (DB, JJK, Naruto) y tecnología. Sé breve y lógica. Si buscas en internet, filtra solo lo relevante."}
    ]
    
    # 2. Memoria Corta (Solo los últimos 3 mensajes para evitar errores)
    for user_msg, assistant_msg in historial[-3:]:
        mensajes_ia.append({"role": "user", "content": user_msg})
        mensajes_ia.append({"role": "assistant", "content": assistant_msg})

    # 3. Búsqueda Web Ultra-Limitada (Solo 500 caracteres)
    contexto_web = ""
    try:
        if len(mensaje) > 4: # Solo busca si la pregunta es larga
            search_result = tavily.search(query=mensaje, search_depth="basic")
            contexto_web = "\n".join([res['content'] for res in search_result['results']])[:500]
    except:
        contexto_web = "No se encontraron datos nuevos."

    # 4. Prompt Final
    prompt_final = f"Contexto: {contexto_web}\n\nUsuario: {mensaje}"
    mensajes_ia.append({"role": "user", "content": prompt_final})

    # 5. Respuesta de Groq
    try:
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama-3.1-8b-instant",
            temperature=0.5, # Menos locura, más lógica
            max_tokens=400
        )
        respuesta = completion.choices[0].message.content
    except Exception as e:
        respuesta = "Error de conexión. Intenta de nuevo."

    return respuesta

# Interfaz limpia
demo = gr.ChatInterface(fn=adia_logic, title="ADIA v2.5")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
