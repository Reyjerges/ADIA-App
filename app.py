import os
import gradio as gr
from groq import Groq

# 1. Configuración de Cliente
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key:
        return "Jorge, no configuraste la API KEY en Render."

    # Prompt de sistema para que sepa quién eres siempre
    mensajes_api = [{
        "role": "system", 
        "content": "Eres ADIA, la compañera de Jorge. Tienes memoria de la conversación actual. Eres técnica, directa y siempre te diriges a Jorge por su nombre."
    }]
    
    # 2. MEMORIA CORREGIDA: Inyectamos el historial real en el formato de Groq
    # Gradio entrega el historial como una lista de listas: [[user, bot], [user, bot]]
    for chat_pasado in historial:
        user_msg = chat_pasado[0]
        bot_msg = chat_pasado[1]
        if user_msg:
            mensajes_api.append({"role": "user", "content": str(user_msg)})
        if bot_msg:
            mensajes_api.append({"role": "assistant", "content": str(bot_msg)})

    # Añadimos el mensaje actual
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Usamos Llama 3.3 70B para máximo razonamiento
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Respaldo automático al modelo rápido si hay saturación
        try:
            backup = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api
            )
            return backup.choices[0].message.content
        except:
            return f"Jorge, tenemos un error de conexión: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA")
    # No usamos 'type', dejamos que Gradio maneje el historial estándar
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
