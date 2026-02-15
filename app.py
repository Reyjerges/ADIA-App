import os
import gradio as gr
from groq import Groq

# 1. Conexión con Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_core(mensaje, historial):
    # Definimos el mensaje de sistema
    mensajes_para_groq = [
        {"role": "system", "content": "Eres ADIA v1.3, experta en robótica y programación."}
    ]

    # 2. Convertimos el historial de Gradio al formato que Groq entiende
    # Gradio pasa el historial como una lista de listas: [[user, bot], [user, bot]]
    if historial:
        for chat_par in historial:
            user_msg = chat_par[0]
            bot_msg = chat_par[1]
            if user_msg:
                mensajes_para_groq.append({"role": "user", "content": str(user_msg)})
            if bot_msg:
                mensajes_para_groq.append({"role": "assistant", "content": str(bot_msg)})

    # 3. Añadimos el mensaje actual del usuario
    mensajes_para_groq.append({"role": "user", "content": str(mensaje)})

    try:
        # 4. Llamada a Groq (Asegúrate de que el modelo sea el correcto)
        respuesta_ia = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_para_groq, # Aquí pasamos la lista limpia
            temperature=0.5
        )
        return respuesta_ia.choices[0].message.content
    except Exception as e:
        return f"❌ ERROR TÉCNICO: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks() as app:
    gr.Markdown("# ADIA v1.3")
    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(placeholder="Escribe aquí...")
    btn = gr.Button("ENVIAR")

    def responder(texto, chat_historial):
        # Llamamos a la función y guardamos la respuesta
        respuesta = adia_core(texto, chat_historial)
        chat_historial.append((texto, respuesta))
        return "", chat_historial

    btn.click(responder, [msg, chatbot], [msg, chatbot])
    msg.submit(responder, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 7860))
    app.launch(server_name="0.0.0.0", server_port=puerto)
