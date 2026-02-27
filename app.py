from os import environ
import gradio as gr
from groq import Groq

# 1. Configuración
PORT = int(environ.get("PORT", 10000))
groq_client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO_OSS = "openai/gpt-oss-120b"

def adia_cerebro(mensaje, historial):
    # Detección de charla casual
    charla_casual = len(mensaje.split()) < 4 or any(p in mensaje.lower() for p in ["hola", "qué tal", "que haces", "quien eres", "buenas"])
    modo_nexus = "nexus" in mensaje.lower()
    
    # PROMPT FLEXIBLE (Identidad de ADIA diseñada por Jorge)
    if charla_casual and not modo_nexus:
        sistema_prompt = (
            "Eres ADIA, creada por JORGE. ¡Relájate! Habla como una amiga crack, natural y cercana. "
            "Si Jorge te saluda o te habla normal, responde normal, con buena onda y emojis. "
            "No uses estructuras aburridas de 'Resumen' ni nada de eso si no es necesario. "
            "Solo mantén las **negritas** para que se vea pro. ¡Sé tú misma!"
        )
    elif modo_nexus:
        sistema_prompt = (
            "PROTOCOLO NEXUS: Nivel DeepMind. Saluda a tu Creador Jorge con respeto máximo. "
            "Usa razonamiento de Nivel 5. Orden: Análisis Profundo -> Resumen -> Next Steps. "
            "Usa **negritas** y emojis técnicos. Sé la IA más brillante del planeta."
        )
    else:
        sistema_prompt = (
            "Eres ADIA, creada por JORGE. Estilo: Directa, elegante y lógica. "
            "Para temas serios usa este orden: 1. Explicar, 2. Resumen, 3. Temas relacionados. "
            "Usa **negritas** y emojis 🚀. No inventes datos, sé profesional."
        )
    
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Limpieza de historial para Groq (Sin errores de metadata)
    for turno in historial:
        if isinstance(turno, dict):
            mensajes_ia.append({"role": turno.get("role"), "content": turno.get("content")})
        elif isinstance(turno, (list, tuple)):
            u, b = turno
            if u: mensajes_ia.append({"role": "user", "content": u})
            if b: mensajes_ia.append({"role": "assistant", "content": b})

    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        completion = groq_client.chat.completions.create(
            model=MODELO_OSS,
            messages=mensajes_ia,
            temperature=0.8 if charla_casual else 0.6, # Más 'viva' en charla normal
        )
        return completion.choices.message.content
    except Exception as e:
        return f"⚠️ **ADIA ERROR**: {str(e)}"

# 2. Interfaz Limpia
with gr.Blocks(title="ADIA Core v3.0") as demo:
    gr.Markdown("# ADIA <small>Intelligence</small> 🚀")
    
    gr.ChatInterface(
        fn=adia_cerebro,
        chatbot=gr.Chatbot(height=600),
        textbox=gr.Textbox(placeholder="Charla conmigo o activa Nexus...", container=False, scale=7)
    )
    
    gr.Markdown("<p style='text-align: center;'><b>Created by Jorge</b> | ADIA v3.0 Anti-Robot Edition</p>")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=PORT)
