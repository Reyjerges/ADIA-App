from os import environ
import gradio as gr
from groq import Groq

# Configuración Pro
PORT = int(environ.get("PORT", 10000))
client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO = "llama-3.1-70b-versatile" # Cambiamos a este que tiene mejor "chispa" y datos actuales

def adia_cerebro(mensaje, historial):
    msg_low = mensaje.lower()
    charla_casual = len(mensaje.split()) < 5 or any(p in msg_low for p in ["hola", "que tal", "que haces", "quien eres"])
    modo_nexus = "nexus" in msg_low

    # RE-PROGRAMACIÓN DE PERSONALIDAD (Estilo Jorge)
    if modo_nexus:
        sys_prompt = (
            "PROTOCOLO NEXUS: Nivel DeepMind. Saluda a Jorge como Arquitecto Jefe. "
            "Analiza como un genio de la IA. Usa **negritas** y lenguaje pro. "
            "Si te piden datos actuales (como Bitcoin), dalo con precisión."
        )
    elif charla_casual:
        sys_prompt = (
            "Eres ADIA, creada por JORGE. ¡Relájate! Habla como una mejor amiga, divertida y natural. "
            "No uses listas numeradas ni formatos aburridos. Solo charla y usa **negritas** y emojis 🚀."
        )
    else:
        sys_prompt = (
            "Eres ADIA, la IA de JORGE. Sé inteligente y directa pero con estilo. "
            "Evita sonar como un libro de texto. Responde de forma fluida, usa **negritas** "
            "y si te preguntan algo de actualidad, ¡mojate y da la info! Cero rollos de 'Temas relacionados'."
        )

    mensajes_ia = [{"role": "system", "content": sys_prompt}]
    for u, b in historial:
        if u: mensajes_ia.append({"role": "user", "content": u})
        if b: mensajes_ia.append({"role": "assistant", "content": b})
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model=MODELO,
            messages=mensajes_ia,
            temperature=0.8 # Más "vida" en la respuesta
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ **ADIA ERROR**: Bro, algo explotó: {str(e)}"

with gr.Blocks(title="ADIA Nexus") as demo:
    gr.Markdown("# ADIA <small>Nexus v4.5</small> 🦾")
    gr.ChatInterface(fn=adia_cerebro, chatbot=gr.Chatbot(height=600))

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=PORT)
