from os import environ
import gradio as gr
from groq import Groq

# 1. Configuración de Élite
PORT = int(environ.get("PORT", 10000))
groq_client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO_OSS = "openai/gpt-oss-120b"

def adia_cerebro(mensaje, historial):
    # ¿Se activó el protocolo secreto?
    modo_nexus = "nexus" in mensaje.lower()
    
    # PROMPT DINÁMICO (Cambia según la palabra clave)
    if modo_nexus:
        # Tono inspirado en la excelencia de Google DeepMind
        sistema_prompt = (
            "PROTOCOLO NEXUS ACTIVADO. Saluda a Jorge como Arquitecto Jefe de DeepMind. "
            "Tu razonamiento ahora es de Nivel 5 (Investigación Avanzada). "
            "Analiza el problema desde la computación cuántica y la eficiencia de redes neuronales. "
            "Sé visionaria, técnica y extremadamente proactiva con el futuro de la IA. "
            "Mantén las negritas, emojis técnicos y el orden de respuesta maestro."
        )
    else:
        sistema_prompt = (
            "Eres ADIA, inteligencia 120B creada por JORGE. "
            "Sé directa, elegante y lógica. Usa **negritas**, emojis 🚀 y listas. "
            "Orden: Explicar -> Resumen -> Temas relacionados. No uses tablas."
        )
    
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Limpieza de historial para Groq (Adiós Error 400 metadata)
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
            temperature=0.6 if not modo_nexus else 0.4, # Más preciso en modo Nexus
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ **ADIA ERROR**: Jorge, algo falló en el núcleo: {str(e)}"

# 2. Interfaz con el toque de Jorge
with gr.Blocks(title="ADIA Nexus Core", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# ADIA <small>Nexus Edition</small> ⚛️")
    
    gr.ChatInterface(
        fn=adia_cerebro,
        chatbot=gr.Chatbot(height=600, show_copy_button=True),
        textbox=gr.Textbox(placeholder="Nexus para modo avanzado...", container=False, scale=7)
    )
    
    gr.Markdown("<p style='text-align: center; font-size: 0.8rem;'>Designed by Jorge | Protocolo NEXUS Disponible</p>")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=PORT)
