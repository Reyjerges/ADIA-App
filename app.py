import gradio as gr
from groq import Groq
import os

# Configuración del motor de inteligencia
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_core(mensaje, historial):
    sistema = {
        "role": "system", 
        "content": "Eres ADIA v1.2. Experta en IA y programación de ML. Creada por un futuro ingeniero robótico. Responde técnico pero fácil."
    }

    mensajes_validados = [sistema]

    # Procesamos el historial para que ADIA tenga memoria
    if historial:
        for usuario, bot in historial:
            if usuario:
                mensajes_validados.append({"role": "user", "content": str(usuario)})
            if bot:
                mensajes_validados.append({"role": "assistant", "content": str(bot)})

    if mensaje:
        mensajes_validados.append({"role": "user", "content": str(mensaje)})

    try:
        busqueda = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_validados,
            temperature=0.4
        )
        # CORRECCIÓN: Usamos .message.content (estilo objeto)
        return busqueda.choices[0].message.content
    except Exception as e:
        return f"⚠️ ERROR DE SISTEMA: {str(e)}"

# --- INTERFAZ minimalista ---
with gr.Blocks(theme=gr.themes.Soft()) as app:
    gr.Markdown("# ADIA v1.2")
    chatbot = gr.Chatbot(label="Chat con ADIA", height=450)
    
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Escribe algo para ADIA...",
            show_label=False,
            scale=4
        )
        btn = gr.Button("ENVIAR", variant="primary", scale=1)

    limpiar = gr.Button("Reiniciar Memoria")

    # --- LÓGICA DE CONEXIÓN ---
    def responder(m, h):
        respuesta = adia_core(m, h)
        h.append((m, respuesta)) # Guardamos en el historial
        return "", h # Limpiamos el texto y actualizamos chat

    # Eventos: Al dar click o dar Enter
    msg.submit(responder, [msg, chatbot], [msg, chatbot])
    btn.click(responder, [msg, chatbot], [msg, chatbot])
    
    # Botón para borrar todo
    limpiar.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    app.launch()
