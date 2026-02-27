from os import environ
import gradio as gr
from groq import Groq

# 1. Configuración de Élite
PORT = int(environ.get("PORT", 10000))
groq_client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO_OSS = "openai/gpt-oss-120b"

def adia_cerebro(mensaje, historial):
    # Protocolo Secreto Nexus
    modo_nexus = "nexus" in mensaje.lower()
    
    if modo_nexus:
        sistema_prompt = (
            "PROTOCOLO NEXUS ACTIVADO. Saluda a Jorge como Arquitecto Jefe. "
            "Tu razonamiento es de Nivel 5 (DeepMind Style). Analiza con lógica pura. "
            "Usa **negritas**, emojis técnicos y el orden maestro: Explicar -> Resumen -> Relacionados."
        )
    else:
        sistema_prompt = (
            "Eres ADIA, inteligencia 120B creada por JORGE. "
            "Sé directa, elegante y usa razonamiento lógico. No uses rellenos. "
            "Habla con **negritas** y emojis 🚀. Orden: Explicar -> Resumen -> Temas relacionados."
        )
    
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Limpieza de historial para evitar Error 400 (metadata)
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
            temperature=0.6 if not modo_nexus else 0.4,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ **ADIA ERROR**: Jorge, el núcleo falló: {str(e)}"

# 2. Interfaz Blindada (Sin argumentos que den TypeError)
with gr.Blocks(title="ADIA Core v2.6") as demo:
    gr.Markdown("# ADIA <small>Nexus Intelligence</small> ⚛️")
    
    gr.ChatInterface(
        fn=adia_cerebro,
        chatbot=gr.Chatbot(height=600), # Quitamos show_copy_button
        textbox=gr.Textbox(placeholder="Nexus para modo avanzado...", container=False, scale=7)
    )
    
    gr.Markdown("<p style='text-align: center;'><b>Designed by Jorge</b> | Powered by GPT-OSS 120B</p>")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=PORT)
