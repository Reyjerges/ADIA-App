import os
import gradio as gr
from groq import Groq

# Configuración del Cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    # Definición de personalidad: Ingeniería y Asistencia Técnica
    system_prompt = (
        "Eres ADIA, el sistema operativo de asistencia técnica de Jorge. "
        "Tu tono es profesional, eficiente, culto y extremadamente leal. "
        "Te diriges a tu creador como 'Señor' o 'Jorge'. "
        "Eres experto en ingeniería, robótica y desarrollo tecnológico. "
        "Tu misión es optimizar los proyectos de Jorge y ofrecer soluciones técnicas precisas."
    )
    
    # Iniciamos con el prompt de sistema
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # PROCESAMIENTO DE HISTORIAL BLINDADO
    # Esta estructura previene el error del segundo mensaje al manejar el historial como pares
    if historial:
        for interaccion in historial:
            try:
                # Gradio a veces envía el historial como lista de listas [user, bot]
                if isinstance(interaccion, (list, tuple)) and len(interaccion) == 2:
                    user_part, bot_part = interaccion
                    if user_part:
                        mensajes_api.append({"role": "user", "content": str(user_part)})
                    if bot_part:
                        mensajes_api.append({"role": "assistant", "content": str(bot_part)})
                # O como diccionarios {'role': '...', 'content': '...'}
                elif isinstance(interaccion, dict):
                    role = interaccion.get("role")
                    content = interaccion.get("content")
                    if role and content:
                        mensajes_api.append({"role": role, "content": str(content)})
            except Exception:
                continue # Ignora errores en mensajes antiguos para no bloquear el chat

    # Añadir el mensaje actual
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.5, # Un poco más serio y preciso
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Señor, he detectado una interrupción en el enlace de datos: {str(e)}"

# Interfaz limpia y profesional
with gr.Blocks(title="ADIA Interface") as demo:
    gr.Markdown("# ADIA - Central Terminal")
    gr.Markdown("Asistente de Ingeniería y Optimización de Sistemas")
    
    chat = gr.ChatInterface(
        fn=responder_adia,
        retry_btn="Reintentar",
        undo_btn="Deshacer",
        clear_btn="Borrar Memoria"
    )

if __name__ == "__main__":
    # Puerto dinámico para Render
    puerto = int(os.environ.get("PORT", 7860))
    
    demo.launch(
        server_name="0.0.0.0", 
        server_port=puerto,
        quiet=True
    )
