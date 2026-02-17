import os
import gradio as gr
from groq import Groq

# 1. Configuración del Cliente
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: No configuraste la variable GROQ_API_KEY en Render."

    # Personalidad Stark/Compañera
    system_prompt = (
        "Eres ADIA, la ayudante y compañera de Jorge. "
        "Tu objetivo es asistir en tareas y preguntas. "
        "Eres técnica, eficiente y siempre llamas a Jorge por su nombre."
    )
    
    # 2. Construcción de memoria con LIMPIEZA de metadatos
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # Este bucle limpia la basura que Gradio envía y que Groq rechaza
    for entrada in historial:
        if isinstance(entrada, dict):
            # Formato nuevo de Gradio: extraemos solo texto
            rol = entrada.get("role")
            contenido = entrada.get("content")
            if rol and contenido:
                mensajes_api.append({"role": rol, "content": str(contenido)})
        elif isinstance(entrada, (list, tuple)) and len(entrada) == 2:
            # Formato antiguo: [usuario, bot]
            u, b = entrada
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    # Añadir el mensaje actual
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA - Sistema de Inteligencia Artificial")
    chat = gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    # CONFIGURACIÓN DE PUERTO PARA RENDER
    # Render asigna dinámicamente un puerto, por eso usamos os.environ.get
    server_port = int(os.environ.get("PORT", 7860))
    
    print(f"Desplegando ADIA en el puerto: {server_port}")
    
    demo.launch(
        server_name="0.0.0.0", 
        server_port=server_port,
        share=False
    )
