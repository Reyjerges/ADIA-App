import gradio as gr
import requests
import time
import json
import os

# --- CONFIGURATION ---
# The API key is handled automatically by the environment
API_KEY = "" 
MODEL_ID = "gemini-2.5-flash-preview-09-2025"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={API_KEY}"

# --- SYSTEM INSTRUCTIONS ---
SYSTEM_PROMPT = "Eres un asistente virtual experto y amable. Responde siempre en español de forma clara."

def call_gemini_api(prompt, history):
    """
    Handles communication with the Gemini API with exponential backoff.
    """
    messages = []
    
    # Format history for Gemini API (user/model)
    for human, assistant in history:
        if human:
            messages.append({"role": "user", "parts": [{"text": human}]})
        if assistant:
            messages.append({"role": "model", "parts": [{"text": assistant}]})
    
    # Add current prompt
    messages.append({"role": "user", "parts": [{"text": prompt}]})

    payload = {
        "contents": messages,
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        }
    }

    # Exponential backoff implementation (5 retries)
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.post(API_URL, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                try:
                    return result['candidates'][0]['content']['parts'][0]['text']
                except (KeyError, IndexError):
                    return "Error: La API devolvió un formato inesperado."
            
            elif response.status_code == 429:
                # Rate limit hit, wait and retry
                time.sleep(2**i)
                continue
            else:
                return f"Error de la API: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            if i == max_retries - 1:
                return f"Error de conexión: {str(e)}"
            time.sleep(2**i)
    
    return "Se agotaron los reintentos de conexión."

def chat_function(message, history):
    if not message.strip():
        return "Por favor, escribe algo."
    return call_gemini_api(message, history)

# --- GRADIO INTERFACE ---
with gr.Blocks(theme=gr.themes.Soft(), title="Chat IA") as demo:
    gr.Markdown("# 🤖 Mi Asistente Gemini")
    
    chatbot_ui = gr.ChatInterface(
        fn=chat_function,
        chatbot=gr.Chatbot(height=500, show_copy_button=True),
        textbox=gr.Textbox(placeholder="Escribe tu mensaje aquí...", container=False, scale=7),
        submit_btn="Enviar",
        retry_btn="Reintentar",
        undo_btn="Deshacer",
        clear_btn="Borrar chat"
    )

if __name__ == "__main__":
    # Ensure it runs on the correct port for cloud environments
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
