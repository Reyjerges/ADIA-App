import os
import time
import requests
import gradio as gr

# Configuración del Asistente ADIA
# El API Key se deja vacío para que el entorno lo gestione automáticamente
API_KEY = "" 
MODEL_NAME = "llama3-70b-8192"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def call_groq_api(messages):
    """
    Realiza la petición a la API de Groq con lógica de reintentos (Backoff Exponencial).
    """
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

    # Reintentos según requerimiento: 1s, 2s, 4s, 8s, 16s
    delays = [1, 2, 4, 8, 16]
    
    for i, delay in enumerate(delays):
        try:
            response = requests.post(
                GROQ_API_URL, 
                json=payload, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'], None
            
            elif response.status_code in [429, 500, 502, 503, 504]:
                if i < len(delays) - 1:
                    time.sleep(delay)
                    continue
                else:
                    return None, f"Error {response.status_code}: ADIA está experimentando mucha carga."
            else:
                return None, f"Error de API: {response.status_code}"
                
        except Exception as e:
            if i < len(delays) - 1:
                time.sleep(delay)
                continue
            return None, f"Error de conexión: {str(e)}"

    return None, "Error crítico de comunicación."

def chat_interface(message, history):
    """
    Lógica de conversación personalizada para ADIA.
    """
    # Prompt de sistema definiendo la identidad de ADIA
    system_prompt = (
        "Eres ADIA (Asistente Digital de Inteligencia Artificial). "
        "Eres un asistente inteligente, eficiente y amable. "
        "Siempre te presentas como ADIA si te preguntan quién eres."
    )
    
    formatted_history = [{"role": "system", "content": system_prompt}]
    
    for user_msg, bot_msg in history:
        if user_msg: formatted_history.append({"role": "user", "content": user_msg})
        if bot_msg: formatted_history.append({"role": "assistant", "content": bot_msg})
    
    formatted_history.append({"role": "user", "content": message})

    response_text, error = call_groq_api(formatted_history)
    
    if error:
        final_msg = f"⚠️ **Aviso de ADIA:** {error}"
    else:
        final_msg = response_text
    
    history.append((message, final_msg))
    return "", history

# Interfaz de Gradio personalizada para ADIA
with gr.Blocks(theme=gr.themes.Default(primary_hue="blue"), title="ADIA - Asistente Digital") as demo:
    gr.Markdown("""
    # 🤖 ADIA
    ### Asistente Digital de Inteligencia Artificial
    *Desarrollado para asistencia inteligente en tiempo real.*
    """)
    
    chatbot = gr.Chatbot(
        label="Chat con ADIA", 
        height=550,
        show_copy_button=True
    )
    
    with gr.Row():
        msg = gr.Textbox(
            label="Escribe aquí...",
            placeholder="Hola ADIA, ¿en qué puedes ayudarme hoy?",
            scale=8
        )
        submit_btn = gr.Button("Enviar a ADIA", variant="primary", scale=2)
    
    with gr.Row():
        gr.ClearButton([msg, chatbot], value="Limpiar Historial", variant="secondary")

    msg.submit(chat_interface, [msg, chatbot], [msg, chatbot])
    submit_btn.click(chat_interface, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    # Configuración de red y puerto
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
