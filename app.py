import os
import gradio as gr
from groq import Groq

# 1. Configuración de Poder
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key:
        return "Jorge, la cámara de gravedad (API KEY) no está configurada en Render."

    # Identidad técnica y directa para Dragon Ball
    system_prompt = (
        "Eres ADIA, la compañera de Jorge. Tu tono es técnico, directo y serio. "
        "No uses palabras cariñosas. Tu objetivo es ayudar a Jorge con su juego de Dragon Ball. "
        "Hablas sobre GDScript, sprites y mecánicas de pelea de forma eficiente."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # Memoria limpia para evitar errores 400
    for h in historial[-5:]:
        if isinstance(h, (list, tuple)):
            u, b = h
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768", 
            messages=mensajes_api,
            temperature=0.6,
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Jorge, error en los scouts: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA - Dragon Ball Dev")
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    # Render usa el puerto 10000 por defecto
    port = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=port)
