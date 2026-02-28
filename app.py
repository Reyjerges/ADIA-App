from os import environ
import gradio as gr
from groq import Groq

# Configuración Maestra para Render
PORT = int(environ.get("PORT", 10000))
client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO = "openai/gpt-oss-120b"

def adia_cerebro(mensaje, historial):
    msg_low = mensaje.lower()
    charla_casual = len(mensaje.split()) < 4 or any(p in msg_low for p in ["hola", "que tal", "quien eres", "buenas"])
    modo_nexus = "nexus" in msg_low

    # El "Cerebro" que tú diseñaste, Jorge
    if modo_nexus:
        sys_prompt = "PROTOCOLO NEXUS: Nivel DeepMind. Saluda al Arquitecto Jorge. Usa lógica de Nivel 5. Orden: Análisis -> Resumen -> Next Steps. Usa **negritas** y emojis técnicos."
    elif charla_casual:
        sys_prompt = "Eres ADIA, creada por JORGE. Habla como una amiga crack, natural y sin estructuras rígidas. Usa **negritas** y emojis 🚀. ¡Sé humana!"
    else:
        sys_prompt = "Eres ADIA, creada por JORGE. Estilo: Directa y lógica. Orden: 1. Explicar, 2. Resumen, 3. Temas relacionados. Usa **negritas** y emojis 🚀."

    # Limpieza de historial nivel experto (Sin metadatos basura)
    mensajes_ia = [{"role": "system", "content": sys_prompt}]
    for turno in historial:
        if isinstance(turno, dict):
            mensajes_ia.append({"role": turno.get("role"), "content": turno.get("content")})
        elif isinstance(turno, (list, tuple)):
            u, b = turno
            if u: mensajes_ia.append({"role": "user", "content": u})
            if b: mensajes_ia.append({"role": "assistant", "content": b})

    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(model=MODELO, messages=mensajes_ia, temperature=0.7)
        # Acceso corregido para evitar fallos de objeto
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ **ADIA ERROR**: Jorge, hay un fallo en el núcleo: {str(e)}"

# Interfaz limpia sin argumentos obsoletos
with gr.Blocks(title="ADIA Nexus") as demo:
    gr.Markdown("# ADIA <small>Intelligence</small> 🚀")
    gr.ChatInterface(fn=adia_cerebro, chatbot=gr.Chatbot(height=600), type="messages")
    gr.Markdown("<p style='text-align: center;'><b>Designed by Jorge</b> | ADIA v4.0 Perfected</p>")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=PORT)
