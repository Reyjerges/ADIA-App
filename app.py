import os
import gradio as gr
from groq import Groq

# 1. Configuración del Cliente
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: No configuraste la variable GROQ_API_KEY en Render."

    # Personalidad de Ingeniería Robótica (Modo Jarvis/Stark)
    system_prompt = (
        "Eres ADIA, la ayudante y compañera de Jorge. "
        "Tu objetivo es asistir en tareas y preguntas. "
        "Eres técnica, eficiente y siempre llamas a Jorge por su nombre."
    )
    
    # 2. Construcción manual de la memoria
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # Gradio en versiones anteriores pasa el historial como lista de listas [[u, b], [u, b]]
    for h in historial:
        if isinstance(h, (list, tuple)) and len(h) == 2:
            mensajes_api.append({"role": "user", "content": str(h[0])})
            mensajes_api.append({"role": "assistant", "content": str(h[1])})

    # Añadir el mensaje actual
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# --- INTERFAZ SIN EL ARGUMENTO 'TYPE' ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA - IA")
    
    # Eliminamos type="messages" para evitar el TypeError
    chat = gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)
