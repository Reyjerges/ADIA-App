import os
import gradio as gr
from groq import Groq

# Configuración del Cliente - La API Key se gestiona desde las variables de entorno
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    # Definición de personalidad: Ingeniería, Robótica y Asistencia Técnica
    system_prompt = (
        "Eres ADIA, el sistema operativo de asistencia técnica avanzada de Jorge. "
        "Tu tono es profesional, eficiente, culto y extremadamente leal. "
        "Te diriges a tu creador como 'Señor' o 'Jorge'. "
        "Eres un sistema experto en ingeniería mecánica, electrónica, robótica y optimización. "
        "Tu misión es servir como la interfaz principal para el desarrollo de proyectos tecnológicos, "
        "ofreciendo soluciones ingeniosas y precisas."
    )
    
    # Iniciamos con el prompt de sistema
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # PROCESAMIENTO DE HISTORIAL BLINDADO
    # Manejo de historial compatible con múltiples versiones de Gradio
    if historial:
        for interaccion in historial:
            try:
                # Caso 1: Historial como lista de pares [usuario, asistente]
                if isinstance(interaccion, (list, tuple)) and len(interaccion) == 2:
                    user_part, bot_part = interaccion
                    if user_part:
                        mensajes_api.append({"role": "user", "content": str(user_part)})
                    if bot_part:
                        mensajes_api.append({"role": "assistant", "content": str(bot_part)})
                # Caso 2: Historial como diccionarios (Gradio moderno)
                elif isinstance(interaccion, dict):
                    role = interaccion.get("role")
                    content = interaccion.get("content")
                    if role and content:
                        mensajes_api.append({"role": role, "content": str(content)})
            except Exception:
                continue 

    # Añadir el mensaje actual
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.4,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Señor, se ha producido una interrupción en los módulos de lenguaje: {str(e)}"

# Interfaz visual optimizada (Se eliminan argumentos conflictivos como retry_btn)
with gr.Blocks(title="ADIA Interface v2.1") as demo:
    gr.Markdown("# ADIA - Mainframe de Ingeniería")
    gr.Markdown("Sistema de Soporte para Desarrollo Tecnológico y Robótica")
    
    # ChatInterface simplificado para máxima compatibilidad
    chat = gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    # Configuración de puerto para entorno Render
    puerto = int(os.environ.get("PORT", 7860))
    
    demo.launch(
        server_name="0.0.0.0", 
        server_port=puerto,
        quiet=True
    )
