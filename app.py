import gradio as gr
from groq import Groq
import os

# Configuración del motor de inteligencia
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_core(mensaje, historial):
    # Definimos la personalidad de ADIA
    sistema = {
        "role": "system",
        "content": "Eres ADIA v1.2. Experta en IA y programación de ML. Responde técnico pero fácil de entender."
    }

    mensajes_validados = [sistema]

    # Validamos historial
    if historial:
        for item in historial:
            if len(item) == 2:
                usuario, bot = item
                if usuario:
                    mensajes_validados.append({"role": "user", "content": str(usuario)})
                if bot:
                    mensajes_validados.append({"role": "assistant", "content": str(bot)})

    mensajes_validados.append({"role": "user", "content": str(mensaje)})

    try:
        busqueda = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_validados,
            temperature=0.4
        )
        # Tomamos la respuesta directamente
        contenido = busqueda.choices[0].message["content"]
        return contenido
    except Exception as e:
        return f"⚠️ ERROR DE SISTEMA: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Monochrome()) as app:
    gr.Markdown("# 🛡️ ADIA v1.2 | AI & MACHINE LEARNING CORE")

    chatbot = gr.Chatbot(label="Terminal de IA", height=450)
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Comando: ADIA, enséñame Machine Learning...",
            scale=4
        )
        btn = gr.Button("ENVIAR", variant="primary", scale=1)

    limpiar = gr.Button("Reiniciar Memoria")

    # Función de respuesta
    def responder(m, h):
        if not m:
            return "", h
        respuesta = adia_core(m, h)
        h.append((m, respuesta))
        return "", h

    msg.submit(responder, [msg, chatbot], [msg, chatbot])
    btn.click(responder, [msg, chatbot], [msg, chatbot])

    # Limpiar historial correctamente
    limpiar.click(lambda: [], None, chatbot, queue=False)

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=10000)
