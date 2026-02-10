import gradio as gr
from groq import Groq
import os

# Configuración de la API
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_jarvis(mensaje, historial):
    # Iniciamos siempre con el rol de sistema
    mensajes_limpios = [
        {"role": "system", "content": "Eres ADIA v1.2, la IA de ingeniería de Jorge. Responde como Jarvis: técnico y eficiente."}
    ]
    
    # Limpiamos el historial de Gradio para que Groq lo acepte
    # Gradio entrega: [[usuario, bot], [usuario, bot]...]
    for par in historial:
        if par[0]: # Mensaje del usuario
            mensajes_limpios.append({"role": "user", "content": str(par[0])})
        if par[1]: # Respuesta del bot
            mensajes_limpios.append({"role": "assistant", "content": str(par[1])})
    
    # Añadimos el mensaje que acabas de escribir
    mensajes_limpios.append({"role": "user", "content": str(mensaje)})

    try:
        # Llamada a la IA
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_limpios,
            temperature=0.5
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error de conexión: {str(e)}"

# Interfaz simplificada pero con estilo oscuro
with gr.Blocks(theme=gr.themes.Monochrome()) as app:
    gr.Markdown("# 🛡️ ADIA v1.2 | JARVIS CORE")
    chatbot = gr.Chatbot(label="Terminal", height=400)
    msg = gr.Textbox(placeholder="Ingrese comando, Señor...")
    clear = gr.Button("Limpiar Terminal")

    def responder(m, h):
        respuesta = adia_jarvis(m, h)
        h.append((m, respuesta))
        return "", h

    msg.submit(responder, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=10000)
    
