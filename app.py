import os
import gradio as gr
from groq import Groq

# Configuración
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key: return "Jorge, falta la API KEY."

    # Identidad limpia y directa
    mensajes_api = [{"role": "system", "content": "Eres ADIA, la compañera de Jorge. Hablas de forma natural, técnica y directa. NUNCA uses palabras cariñosas. Siempre llamas a Jorge por su nombre."}]
    
    # Memoria de texto puro para evitar errores de metadatos
    for h in historial[-5:]:
        if isinstance(h, (list, tuple)):
            u, b = h
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Nuevo modelo oficial de Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_api,
            temperature=0.5,
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Respaldo automático al modelo instantáneo si el grande falla
        try:
            backup = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api
            )
            return backup.choices[0].message.content
        except:
            return f"Jorge, el sistema está saturado. Error: {str(e)}"

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA")
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=port)
