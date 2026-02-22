import os
import gradio as gr
from groq import Groq

# Solo necesitamos Groq para esta prueba de estabilidad
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_logic(mensaje, historial):
    # 1. Sistema ultra ligero
    mensajes_ia = [{"role": "system", "content": "Eres ADIA. Responde de forma corta y precisa."}]
    
    # 2. Solo recordamos los últimos 2 mensajes para no saturar
    for user_msg, assistant_msg in historial[-2:]:
        mensajes_ia.append({"role": "user", "content": user_msg})
        mensajes_ia.append({"role": "assistant", "content": assistant_msg})

    mensajes_ia.append({"role": "user", "content": mensaje})

    # 3. Respuesta directa
    try:
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama-3.1-8b-instant",
            max_tokens=200 # Muy ligero
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error de Ki: {str(e)}"

# Interfaz básica
demo = gr.ChatInterface(fn=adia_logic, title="ADIA v2.6 - Test de Estabilidad")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
