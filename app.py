from os import environ
import gradio as gr
from groq import Groq

# Configuración de Puerto para Render
PORT = int(environ.get("PORT", 10000))
# Asegúrate de tener GROQ_API_KEY en las Environment Variables de Render
client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO = "llama-3.3-70b-versatile"

def adia_cerebro(mensaje, historial):
    msg_low = mensaje.lower()
    charla_casual = len(mensaje.split()) < 5 or any(p in msg_low for p in ["hola", "que tal", "que haces", "quien eres"])
    modo_nexus = "nexus" in msg_low

    if modo_nexus:
        sys_prompt = "PROTOCOLO NEXUS: Nivel DeepMind. Saluda a Jorge como Arquitecto Jefe. Analiza como un genio. Usa **negritas**."
    elif charla_casual:
        sys_prompt = "Eres ADIA, creada por JORGE. Habla como una mejor amiga, divertida. Usa **negritas** y emojis 🚀."
    else:
        sys_prompt = "Eres ADIA, la IA de JORGE. Inteligente y directa. Usa **negritas**."

    mensajes_ia = [{"role": "system", "content": sys_prompt}]
    
    # Gradio maneja el historial automáticamente en ChatInterface
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
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ **ADIA ERROR**: {str(e)}"

# Interfaz simplificada para evitar errores de versión
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# ADIA <small>Nexus v4.5</small> 🦾")
    gr.ChatInterface(
        fn=adia_cerebro,
        # Quitamos 'show_copy_button' para máxima compatibilidad
        chatbot=gr.Chatbot(height=500),
    )

if __name__ == "__main__":
    # Importante: server_name y server_port para que Render detecte el puerto
    demo.launch(server_name="0.0.0.0", server_port=PORT, share=False)
