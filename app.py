import os
import gradio as gr
from groq import Groq

# 1. Configuración de Poder
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key:
        return "Jorge, falta la clave API en Render."

    # Identidad básica y directa
    mensajes_api = [{"role": "system", "content": "Eres ADIA, la compañera de Jorge. Hablas de forma natural y directa. Siempre llamas a Jorge por su nombre."}]
    
    # 2. LIMPIEZA DE METADATOS (Para evitar el error 400)
    for h in historial[-5:]:
        # Extraemos solo el texto, ignorando diccionarios de metadatos
        user_text = h[0] if isinstance(h[0], str) else h[0].get("text", "") if isinstance(h[0], dict) else ""
        bot_text = h[1] if isinstance(h[1], str) else h[1].get("text", "") if isinstance(h[1], dict) else ""
        
        if user_text:
            mensajes_api.append({"role": "user", "content": str(user_text)})
        if bot_text:
            mensajes_api.append({"role": "assistant", "content": str(bot_text)})

    # Mensaje actual (solo texto)
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Mixtral es el más estable para evitar errores de cuota
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768", 
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Respaldo rápido
        try:
            backup = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api
            )
            return backup.choices[0].message.content
        except:
            return f"Jorge, hubo un problema: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA")
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
