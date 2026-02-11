import gradio as gr
from groq import Groq
import os

# Configuración del motor de inteligencia
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_core(mensaje, historial):
    # Definimos la personalidad de ADIA: Experta en IA y tareas
    sistema = {
        "role": "system", 
        "content": "Eres ADIA v1.2. Tu especialidad es el Machine Learning, la programación de IA en Python y ayudar a Jorge con sus tareas escolares. Responde de forma técnica pero fácil de entender."
    }
    
    # --- PROCESO DE LIMPIEZA PARA EVITAR EL ERROR DE FORMATO ---
    mensajes_validados = [sistema]
    
    # Convertimos el historial de Gradio al formato exacto que pide la API
    for usuario, bot in historial:
        if usuario:
            mensajes_validados.append({"role": "user", "content": str(usuario)})
        if bot:
            mensajes_validados.append({"role": "assistant", "content": str(bot)})
    
    # Añadimos el mensaje actual
    mensajes_validados.append({"role": "user", "content": str(mensaje)})

    try:
        # Llamada a la inteligencia de Groq
        busqueda = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_validados,
            temperature=0.4 # Menos locura, más precisión técnica
        )
        return busqueda.choices[0].message.content
    except Exception as e:
        return f"⚠️ ERROR DE SISTEMA: {str(e)}"

# --- INTERFAZ DE LABORATORIO (Simplificada y estable) ---
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

    # Lógica de funcionamiento
    def responder(m, h):
        if not m: return "", h
        respuesta = adia_core(m, h)
        h.append((m, respuesta))
        return "", h

    msg.submit(responder, [msg, chatbot], [msg, chatbot])
    btn.click(responder, [msg, chatbot], [msg, chatbot])
    limpiar.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    # Puerto configurado para Render
    app.launch(server_name="0.0.0.0", server_port=10000)
