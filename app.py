# STARK INDUSTRIES - ADIA MAIN INTERFACE
# Archivo: app.py
# Función: Sistema central de IA con Groq y Gradio optimizado.

import os
import gradio as gr
from groq import Groq

# Configuración del Cliente
# Nota: La API Key se obtiene de las variables de entorno para máxima seguridad.
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    """
    Motor de respuesta principal de ADIA.
    Utiliza Llama 3 para un procesamiento de lenguaje natural avanzado.
    """
    # Verificación de seguridad de la API
    if not api_key:
        return "Señor Jorge, el mainframe no detecta la GROQ_API_KEY. Por favor, configúrela en las variables de entorno para continuar."

    # Configuración de personalidad y directivas del sistema
    system_prompt = (
        "Eres ADIA, el sistema operativo de asistencia técnica avanzada de Jorge. "
        "Tu tono es profesional, eficiente, culto y extremadamente leal. "
        "Te diriges a tu creador como 'Señor Jorge'. "
        "Eres un sistema experto en ingeniería mecánica, electrónica y robótica. "
        "Tu misión es ayudar a Jorge y ser su compañera, "
        "ofreciendo soluciones precisas y seguras. Responde siempre de forma clara y estructurada."
    )
    
    # Construcción del contexto de la conversación
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # Integración del historial de forma segura
    if historial:
        for interaccion in historial:
            # Soporte para diferentes formatos de historial en Gradio
            if isinstance(interaccion, (list, tuple)):
                user_msg, bot_msg = interaccion
                if user_msg: mensajes_api.append({"role": "user", "content": str(user_msg)})
                if bot_msg: mensajes_api.append({"role": "assistant", "content": str(bot_msg)})
            elif isinstance(interaccion, dict):
                mensajes_api.append({"role": interaccion.get("role"), "content": str(interaccion.get("content"))})

    # Añadir el comando actual del usuario
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Petición al motor de inferencia
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.5,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Señor Jorge, se ha detectado una anomalía en el enlace de datos: {str(e)}"

# --- DISEÑO DE LA INTERFAZ DE USUARIO (STARK HUD) ---
with gr.Blocks(title="ADIA Interface v3.0", theme=gr.themes.Default(primary_hue="cyan", secondary_hue="slate")) as demo:
    with gr.Column(elem_id="main-container"):
        gr.Markdown(
            """
            # 🦾 ADIA - IA
            ### ayudante IA
            ---
            """
        )
        
        with gr.Row():
            with gr.Column(scale=4):
                # Interfaz de Chat optimizada
                chat = gr.ChatInterface(
                    fn=responder_adia,
                    description="[ESTADO: LÍNEA] Esperando instrucciones de ingeniería, Jorge.",
                    retry_btn="Reintentar",
                    undo_btn="Deshacer",
                    clear_btn="Limpiar Terminal"
                )
            
            with gr.Column(scale=1):
                # Panel de Control lateral
                gr.Markdown("### ESTADO")
                gr.Image(value="https://img.icons8.com/nolan/256/iron-man.png", label="Reactor Ark", show_label=False)
                
                status_labels = gr.Label(
                    value={
                        "Núcleo de IA": "OPERATIVO",
                        "Enlace Groq": "ACTIVO",
                        "Seguridad": "NIVEL 5"
                    },
                    label="Diagnóstico de Sistemas"
                )
                
                gr.Markdown(
                    """
                    ---
                    **AVISO:** Todos los protocolos de seguridad están activos para proteger la integridad del laboratorio.
                    """
                )

if __name__ == "__main__":
    # Configuración de puerto dinámica para entornos como Render
    server_port = int(os.environ.get("PORT", 7860))
    
    print(">>> ADIA OS v3.0 <<<")
    print(f">>> Iniciando mainframe para el Señor Jorge en puerto {server_port}...")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=server_port,
        quiet=True
    )
            
