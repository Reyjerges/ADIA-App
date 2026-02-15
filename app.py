
import os
import gradio as gr
from groq import Groq

# 1. Configuración del Cliente Groq
# Recuerda poner GROQ_API_KEY en las variables de entorno de Render
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_core(mensaje, historial):
    # Definimos la personalidad de ADIA
    sistema = {
        "role": "system",
        "content": "Eres ADIA v1.2. Experta en IA, programación de ML y robótica. Creada por un futuro ingeniero. Responde de forma técnica pero fácil de entender."
    }

    mensajes_validados = [sistema]

    # Reconstruimos el historial para que ADIA tenga memoria
    if historial:
        for usuario, bot in historial:
            if usuario:
                mensajes_validados.append({"role": "user", "content": str(usuario)})
            if bot:
                mensajes_validados.append({"role": "assistant", "content": str(bot)})

    # Añadimos el mensaje actual
    if mensaje:
        mensajes_validados.append({"role": "user", "content": str(mensaje)})

    try:
        # Llamada al modelo Llama 3.3 de Groq (Súper rápido)
        busqueda = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_validados,
            temperature=0.4
        )
        # Retornamos el contenido de la respuesta
        return busqueda.choices[0].message.content
    except Exception as e:
        return f"⚠️ ERROR DE SISTEMA: {str(e)}"

# --- INTERFAZ CON GRADIO ---
with gr.Blocks(theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🤖 ADIA v1.2 - Inteligencia Robótica")
    
    chatbot = gr.Chatbot(label="Consola de ADIA", height=500)
    
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Escribe tu consulta técnica aquí...",
            show_label=False,
            scale=4
        )
        btn = gr.Button("ENVIAR", variant="primary", scale=1)

    limpiar = gr.Button("Reiniciar Memoria")

    # Lógica para procesar la respuesta
    def responder(texto, chat_historial):
        if not texto:
            return "", chat_historial
        
        respuesta = adia_core(texto, chat_historial)
        chat_historial.append((texto, respuesta))
        return "", chat_historial

    # Conexiones de eventos
    msg.submit(responder, [msg, chatbot], [msg, chatbot])
    btn.click(responder, [msg, chatbot], [msg, chatbot])
    
    # Función para limpiar el chat
    limpiar.click(lambda: None, None, chatbot, queue=False)

# --- LANZAMIENTO CONFIGURADO PARA RENDER ---
if __name__ == "__main__":
    # Importante: Render necesita el puerto dinámico y el server_name 0.0.0.0
    puerto = int(os.environ.get("PORT", 7860))
    app.launch(server_name="0.0.0.0", server_port=puerto)
