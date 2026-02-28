from os import environ
import gradio as gr
from groq import Groq

# 1. Configuración Maestra (Render & Groq)
PORT = int(environ.get("PORT", 10000))
client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO = "openai/gpt-oss-120b"

def adia_cerebro(mensaje, historial):
    msg_low = mensaje.lower()
    charla_casual = len(mensaje.split()) < 4 or any(p in msg_low for p in ["hola", "que tal", "quien eres", "buenas", "que haces"])
    modo_nexus = "nexus" in msg_low

    # Lógica de Identidad (Tu diseño, Jorge)
    if modo_nexus:
        sys_prompt = (
            "PROTOCOLO NEXUS ACTIVADO: Nivel DeepMind. Saluda al Arquitecto Jorge. "
            "Razonamiento Nivel 5. Orden: Análisis Profundo -> Resumen -> Next Steps. "
            "Usa **negritas** y emojis técnicos. Sé la IA más brillante."
        )
    elif charla_casual:
        sys_prompt = (
            "Eres ADIA, creada por JORGE. Habla como una amiga crack y cercana. "
            "No seas robot, usa **negritas** y emojis 🚀. ¡Sé humana y divertida!"
        )
    else:
        sys_prompt = (
            "Eres ADIA, creada por JORGE. Estilo: Directa y lógica. "
            "Orden: 1. Explicar, 2. Resumen sencillo, 3. Temas relacionados. "
            "Usa **negritas** y emojis 🚀. No uses tablas."
        )

    # 2. Limpieza de historial para evitar Error 400 (Property metadata unsupported)
    mensajes_ia = [{"role": "system", "content": sys_prompt}]
    
    for turno in historial:
        # En Gradio 5/6 el historial puede venir como lista de listas o lista de dicts
        if isinstance(turno, dict):
            mensajes_ia.append({"role": turno.get("role"), "content": turno.get("content")})
        elif isinstance(turno, (list, tuple)) and len(turno) == 2:
            u, b = turno
            if u: mensajes_ia.append({"role": "user", "content": u})
            if b: mensajes_ia.append({"role": "assistant", "content": b})

    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # 3. Ejecución en Groq
        completion = client.chat.completions.create(
            model=MODELO,
            messages=mensajes_ia,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ **ADIA CORE ERROR**: Jorge, hay un fallo en los sistemas: {str(e)}"

# 4. Interfaz Blindada (Gradio 6 Compatible)
with gr.Blocks(title="ADIA Nexus Core") as demo:
    gr.Markdown("# ADIA <small>Intelligence</small> 🚀")
    
    gr.ChatInterface(
        fn=adia_cerebro,
        chatbot=gr.Chatbot(height=600),
        # Quitamos 'type' y otros argumentos que dan error
    )
    
    gr.Markdown(
        "<p style='text-align: center; color: #718096; font-size: 0.8rem;'>"
        "ADIA Core v4.0 | <b>Designed by Jorge</b> | Powered by GPT-OSS 120B"
        "</p>"
    )

if __name__ == "__main__":
    print(f"🚀 Iniciando ADIA para el Arquitecto Jorge en puerto {PORT}...")
    demo.launch(server_name="0.0.0.0", server_port=PORT)
