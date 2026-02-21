import os
import gradio as gr
from groq import Groq

# 1. Configuración de Poder
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key: return "Jorge, falta la API KEY."

    # Identidad técnica y directa
    system_prompt = "Eres ADIA, la compañera de Jorge. Eres técnica, directa y seria. Llama a Jorge por su nombre."
    
    # 2. MEMORIA DE ALTO RENDIMIENTO: Solo enviamos los últimos 3 mensajes
    # Esto es VITAL para que el 70B no te dé error de límite de tokens (TPM)
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    for h in historial[-3:]:
        if isinstance(h, (list, tuple)):
            u, b = h
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # MODELO: Llama 3.3 70B (El más inteligente y rápido en Groq actualmente)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_api,
            temperature=0.6,
            max_tokens=600 # Respuesta concisa para no quemar la cuota
        )
        return completion.choices.message.content
    except Exception as e:
        # Si falla por límite, te pide una pausa de 10 seg
        return f"Jorge, el 70B está saturado. Espera 10 segundos para el siguiente ataque. (Error: {str(e)})"

# --- INTERFAZ ---
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 ADIA - Llama 3.3 70B")
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=port)
