from os import environ
import gradio as gr
from groq import Groq

# Configuración Pro
PORT = int(environ.get("PORT", 10000))
# Asegúrate de poner tu llave en las "Environment Variables" de Render como GROQ_API_KEY
client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO = "llama-3.3-70b-versatile" # Actualizado a la versión más potente y rápida

def adia_cerebro(mensaje, historial):
    # Gradio pasa el historial como lista de listas [[user, bot], ...]
    # Si el historial está vacío, inicializamos
    if historial is None:
        historial = []

    msg_low = mensaje.lower()
    charla_casual = len(mensaje.split()) < 5 or any(p in msg_low for p in ["hola", "que tal", "que haces", "quien eres"])
    modo_nexus = "nexus" in msg_low

    # RE-PROGRAMACIÓN DE PERSONALIDAD
    if modo_nexus:
        sys_prompt = "PROTOCOLO NEXUS: Nivel DeepMind. Saluda a Jorge como Arquitecto Jefe. Analiza como un genio. Usa **negritas**."
    elif charla_casual:
        sys_prompt = "Eres ADIA, creada por JORGE. Habla como una mejor amiga, divertida. Usa **negritas** y emojis 🚀."
    else:
        sys_prompt = "Eres ADIA, la IA de JORGE. Inteligente y directa. Usa **negritas** y mójate con la info."

    mensajes_ia = [{"role": "system", "content": sys_prompt}]
    
    # Formatear historial correctamente para Groq
    for user_msg, bot_msg in historial:
        mensajes_ia.append({"role": "user", "content": user_msg})
        mensajes_ia.append({"role": "assistant", "content": bot_msg})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model=MODELO,
            messages=mensajes_ia,
            temperature=0.8
        )
        # CORRECCIÓN: Groq usa .choices[0].message.content (no .choices.message)
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ **ADIA ERROR**: Bro, algo explotó: {str(e)}"

# Interfaz mejorada
with gr.Blocks(title="ADIA Nexus", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# ADIA <small>Nexus v4.5</small> 🦾")
    gr.ChatInterface(
        fn=adia_cerebro, 
        chatbot=gr.Chatbot(height=500, show_copy_button=True),
        retry_btn="Reintentar",
        undo_btn="Borrar último",
        clear_btn="Limpiar todo"
    )

if __name__ == "__main__":
    # Importante para Render: server_name="0.0.0.0"
    demo.launch(server_name="0.0.0.0", server_port=PORT)
