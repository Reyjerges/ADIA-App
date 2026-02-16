import os
import gradio as gr
from groq import Groq

# Cliente de Groq - Se requiere la variable de entorno GROQ_API_KEY en Render
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    # Definición de la personalidad y rol de ADIA
    system_prompt = (
        "Eres ADIA, el sistema operativo de asistencia técnica de Jorge. "
        "Tu tono es profesional, eficiente, culto y leal. "
        "Te diriges a tu creador como 'Jorge'. "
        "Eres experto en robotica. "
        "Tu misión es ayudar a Jorge."
    )
    
    # Construcción de la lista de mensajes para la IA
    mensajes_para_api = [{"role": "system", "content": system_prompt}]
    
    # PROCESAMIENTO DE MEMORIA UNIVERSAL
    # Este bloque evita errores de tipo al procesar el historial de Gradio
    if historial:
        for interaccion in historial:
            try:
                # Soporte para formato de diccionario (versiones nuevas)
                if isinstance(interaccion, dict):
                    role = interaccion.get("role")
                    content = interaccion.get("content")
                    if role and content:
                        mensajes_para_api.append({"role": role, "content": str(content)})
                
                # Soporte para formato de lista [usuario, asistente] (versiones clásicas)
                elif isinstance(interaccion, (list, tuple)) and len(interaccion) == 2:
                    usr_msg, bot_msg = interaccion
                    if usr_msg:
                        mensajes_para_api.append({"role": "user", "content": str(usr_msg)})
                    if bot_msg:
                        mensajes_para_api.append({"role": "assistant", "content": str(bot_msg)})
            except Exception:
                # Si un mensaje da error, se salta para no bloquear la respuesta actual
                continue

    # Añadir el mensaje actual del usuario
    mensajes_para_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Petición a los servidores de Groq (Llama 3.1)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_para_api,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Señor, he detectado una anomalía en los protocolos: {str(e)}"

# Configuración de la interfaz visual
with gr.Blocks(title="ADIA - Sistema de Asistencia") as demo:
    gr.Markdown("# ADIA: Centro de Control")
    gr.Markdown("### Protocolo de Asistencia Personalizado")
    
    chat = gr.ChatInterface(
        fn=responder_adia,
        retry_btn="Reintentar",
        undo_btn="Deshacer",
        clear_btn="Limpiar Memoria"
    )

# Ejecución del servidor
if __name__ == "__main__":
    # Render usa una variable de entorno llamada PORT para asignar el puerto
    puerto = int(os.environ.get("PORT", 7860))
    
    print(f"Iniciando ADIA en el puerto {puerto}...")
    
    # Es fundamental usar server_name="0.0.0.0" para que Render pueda acceder
    demo.launch(
        server_name="0.0.0.0", 
        server_port=puerto,
        share=False
    )
