import os
import gradio as gr
from groq import Groq

# 1. Configuración limpia
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key:
        return "Jorge, no detecto la GROQ_API_KEY en las variables de Render."

    # Prompt directo y personal
    system_prompt = "Eres ADIA, la compañera de Jorge. Habla de forma natural, técnica y directa. Llama a Jorge por su nombre."
    
    # Memoria ultra-ligera (Solo los últimos 3 mensajes para evitar el error de Groq)
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    for h in historial[-3:]:
        # Gradio pasa el historial como listas [usuario, bot]
        if isinstance(h, (list, tuple)):
            mensajes_api.append({"role": "user", "content": h[0]})
            mensajes_api.append({"role": "assistant", "content": h[1]})

    mensajes_api.append({"role": "user", "content": mensaje})

    try:
        # Usamos el modelo 70B pero con límites estrictos de tokens para que no falle
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=1000 
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Si el 70B falla, usamos el 8B rápido como respaldo automático
        try:
            backup = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api
            )
            return backup.choices[0].message.content
        except:
            return "Jorge, Groq está saturado. Dame un respiro de 30 segundos y volvemos."

# --- INTERFAZ SIN ERRORES ---
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 ADIA")
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    # Render detectará este puerto automáticamente
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
