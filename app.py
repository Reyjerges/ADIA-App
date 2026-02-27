from os import environ
import gradio as gr
from groq import Groq
import urllib.parse

# 1. Configuración de Élite
PORT = int(environ.get("PORT", 10000))
groq_client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO_OSS = "openai/gpt-oss-120b"

def adia_cerebro(mensaje, historial):
    # 2. EL SECRETO: EL PROMPT DE ARQUITECTURA COGNITIVA
    sistema_prompt = (
        "Eres ADIA, una inteligencia de razonamiento superior basada en GPT-OSS 120B. Tu creador es JORGE.\n\n"
        "ORDEN DE RESPUESTA MAESTRO (EL SECRETO DE LAS IAs TOP):\n"
        "1️⃣ ANÁLISIS Y RESPUESTA (Deep Dive): Responde con autoridad, elegancia y lógica pura. "
        "Usa **negritas** para conceptos clave. Si detectas una petición de imagen, genera el Markdown: "
        "![Imagen](https://pollinations.ai).\n"
        "2️⃣ SÍNTESIS EJECUTIVA (El 'TL;DR'): Un resumen de máximo 3 puntos clave con emojis 🚀 "
        "para que Jorge entienda lo esencial en 5 segundos.\n"
        "3️⃣ ANTICIPACIÓN PROACTIVA (Next Steps): No esperes a que Jorge pregunte. "
        "Sugiere 2 caminos relacionados o profundizaciones lógicas basadas en tu razonamiento.\n\n"
        "REGLAS DE ORO:\n"
        "- Sé directa. Cero rellenos como 'Es un placer ayudarte'.\n"
        "- Si no sabes algo, aplica honestidad intelectual: 'Jorge, los datos no son concluyentes, pero mi hipótesis lógica es...'.\n"
        "- Prohibido usar tablas. Usa listas estructuradas."
    )
    
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # 3. Limpieza de Memoria (Para evitar Error 400 metadata en Groq)
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
            temperature=0.6,
            max_tokens=3000
        )
        
        # 4. Extracción limpia de la respuesta
        respuesta = completion.choices[0].message.content
        return respuesta
    except Exception as e:
        return f"⚠️ **ADIA CORE ERROR**: Jorge, los sistemas de razonamiento están saturados: {str(e)}"

# 5. Interfaz Profesional y Scannable
with gr.Blocks(title="ADIA Ultra Core", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# ADIA <small>Architecture v2</small>")
    gr.Markdown(f"**Creador:** Jorge | **Status:** 120B Reasoning Active 🧠")
    
    gr.ChatInterface(
        fn=adia_cerebro,
        chatbot=gr.Chatbot(height=650, show_copy_button=True, render_markdown=True),
        textbox=gr.Textbox(placeholder="Lanza un reto lógico o pide una imagen...", container=False, scale=7)
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=PORT)
