import gradio as gr
import requests
import time
import json

# --- CONFIGURACIÓN DEL MODELO ---
# El API Key se maneja automáticamente en el entorno de ejecución.
API_KEY = "" 
MODEL_ID = "gemini-2.5-flash-preview-09-2025"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={API_KEY}"

# --- INSTRUCCIONES DEL SISTEMA ---
SYSTEM_PROMPT = """
Eres un asistente virtual experto, amable y servicial. 
Tus respuestas deben ser claras, precisas y en español.
Si no sabes algo, admítelo con honestidad.
Mantén siempre un tono profesional pero cercano.
"""

def call_gemini_api(prompt, history):
    """
    Función para comunicarse con la API de Gemini con manejo de errores y reintentos.
    """
    # Construimos el historial para que el modelo tenga contexto
    messages = []
    
    # Añadimos los mensajes previos del historial de Gradio
    for human, assistant in history:
        messages.append({"role": "user", "parts": [{"text": human}]})
        messages.append({"role": "model", "parts": [{"text": assistant}]})
    
    # Añadimos la pregunta actual
    messages.append({"role": "user", "parts": [{"text": prompt}]})

    payload = {
        "contents": messages,
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        }
    }

    # Implementación de reintentos con Backoff Exponencial
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.post(API_URL, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                # Extraemos el texto de la respuesta
                return result['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 429:
                # Error de cuota (Too Many Requests)
                time.sleep(2**i)
                continue
            else:
                return f"Error del servidor: {response.status_code} - {response.text}"
        except Exception as e:
            if i == max_retries - 1:
                return f"Error de conexión tras varios intentos: {str(e)}"
            time.sleep(2**i)

def chat_function(message, history):
    """
    Función principal que conecta la interfaz con la lógica de la API.
    """
    if not message.strip():
        return "Por favor, escribe algo."
    
    return call_gemini_api(message, history)

# --- INTERFAZ DE USUARIO (GRADIO) ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown(f"# Asistente Inteligente ({MODEL_ID})")
    gr.Markdown("Este chat utiliza inteligencia artificial para responder tus dudas con contexto de conversación.")
    
    chatbot = gr.ChatInterface(
        fn=chat_function,
        textbox=gr.Textbox(
            placeholder="Hazme una pregunta...",
            container=False, 
            scale=7
        ),
        retry_btn="Reintentar",
        undo_btn="Deshacer",
        clear_btn="Limpiar Chat",
    )

if __name__ == "__main__":
    # Importante para despliegue: server_name="0.0.0.0"
    demo.launch(server_name="0.0.0.0")
