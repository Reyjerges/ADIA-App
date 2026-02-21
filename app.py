import os
import gradio as gr
from groq import Groq

# 1. Configuración de Poder
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key: return "Jorge, falta la API KEY en Render."

    # Identidad técnica y directa
    system_prompt = "Eres ADIA, la compañera de Jorge. Eres técnica, directa y seria. Llama a Jorge por su nombre."
    
    # 2. MEMORIA OPTIMIZADA: Solo enviamos los últimos 3 mensajes para no saturar tokens
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    for h in historial[-3:]:
        # Gradio entrega el historial como listas [usuario, bot]
        if isinstance(h, (list, tuple)):
            u, b = h
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # MODELO: Llama 3.3 70B Versatile
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_api,
            temperature=0.6,
            max_tokens=800
        )
        # CORRECCIÓN VITAL: Acceso por índice [0] para evitar el error de 'list'
        return completion.choices[0].message.content
    except Exception as e:
        return f"Jorge, hubo un lío técnico: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA - Llama 3.3 70B")
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=port)
