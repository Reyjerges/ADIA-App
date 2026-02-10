import os
import time
import requests
import gradio as gr

# Configuración - Render tomará la API_KEY de las variables de entorno
API_KEY = os.getenv("GROQ_API_KEY", "") 
MODEL_NAME = "llama3-70b-8192"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def call_groq_api(messages):
    if not API_KEY:
        return None, "Error: Configura GROQ_API_KEY en las variables de entorno de Render."

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    delays = [1, 2, 4, 8, 16]
    for i, delay in enumerate(delays):
        try:
            response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'], None
            elif response.status_code in [429, 500, 502, 503, 504]:
                time.sleep(delay)
            else:
                return None, f"Error {response.status_code}"
        except Exception as e:
            if i == len(delays) - 1: return None, str(e)
            time.sleep(delay)
    return None, "Error de conexión persistente."

def respond(message, history):
    system_prompt = "Eres ADIA, un asistente digital inteligente y amable."
    
    # Construcción de mensajes
    messages = [{"role": "system", "content": system_prompt}]
    for user_msg, bot_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})

    bot_message, error = call_groq_api(messages)
    
    if error:
        history.append((message, f"⚠️ {error}"))
    else:
        history.append((message, bot_message))
    
    return "", history

with gr.Blocks(theme=gr.themes.Soft(), title="ADIA") as demo:
    gr.Markdown("# 🤖 ADIA\nAsistente Digital de Inteligencia Artificial")
    
    chatbot = gr.Chatbot(label="Chat con ADIA", height=500)
    
    with gr.Row():
        msg = gr.Textbox(
            label="Mensaje", 
            placeholder="Escribe aquí...", 
            scale=8,
            container=False
        )
        submit_btn = gr.Button("Enviar", variant="primary", scale=2)
    
    gr.ClearButton([msg, chatbot], value="Limpiar")

    # Vinculación corregida
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    submit_btn.click(respond, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    # Importante para Render: server_name="0.0.0.0"
    demo.launch(server_name="0.0.0.0", server_port=7860)
