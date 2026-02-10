import os
import time
import requests
import gradio as gr

# Configuración de Groq
# El API Key se deja vacío para que el entorno lo gestione o el usuario lo asigne
API_KEY = "" 
MODEL_NAME = "llama3-70b-8192"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def call_groq_api(messages):
    """
    Realiza la petición a la API de Groq con lógica de reintentos.
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

    # Implementación de reintentos con Backoff Exponencial
    # 1s, 2s, 4s, 8s, 16s
    delays = [1, 2, 4, 8, 16]
    
    for i, delay in enumerate(delays):
        try:
            response = requests.post(
                GROQ_API_URL, 
                json=payload, 
                headers=headers, 
                timeout=30
            )
            
            # Si es exitoso, devolvemos el contenido
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'], None
            
            # Si hay error de Rate Limit (429) o error de servidor (5xx)
            elif response.status_code in [429, 500, 502, 503, 504]:
                if i < len(delays) - 1:
                    time.sleep(delay)
                    continue
                else:
                    return None, f"Error de Groq tras varios reintentos: {response.status_code}"
            else:
                return None, f"Error de API: {response.status_code} - {response.text}"
                
        except Exception as e:
            if i < len(delays) - 1:
                time.sleep(delay)
                continue
            return None, f"Error de conexión: {str(e)}"

    return None, "Error desconocido al contactar con Groq."

def chat_interface(message, history):
    """
    Gestiona el flujo de la conversación y el historial.
    """
    # Convertir historial de Gradio al formato de OpenAI/Groq
    formatted_history = [
        {"role": "system", "content": "Eres un asistente servicial y preciso que utiliza el modelo Llama 3 a través de Groq."}
    ]
    
    for user_msg, bot_msg in history:
        formatted_history.append({"role": "user", "content": user_msg})
        formatted_history.append({"role": "assistant", "content": bot_msg})
    
    formatted_history.append({"role": "user", "content": message})

    # Llamada a la API
    response_text, error = call_groq_api(formatted_history)
    
    if error:
        # Mostramos el error de forma amigable en el chat
        return history + [[message, f"❌ **Error:** {error}"]]
    
    return history + [[message, response_text]]

# Construcción de la interfaz de usuario
with gr.Blocks(theme=gr.themes.Soft(), title="Llama 3 Groq Chat") as demo:
    gr.Markdown(
        """
        # ⚡ Llama 3 en Groq
        Bienvenido a la interfaz de chat ultrarrápida utilizando el modelo Llama 3-70B de Meta, 
        servido a través de la infraestructura de Groq.
        """
    )
    
    chatbot = gr.Chatbot(
        label="Conversación con Llama 3",
        bubble_full_width=False,
        height=550
    )
    
    with gr.Row():
        msg = gr.Textbox(
            label="Tu mensaje",
            placeholder="Escribe algo para Llama 3...",
            scale=8
        )
        submit_btn = gr.Button("Enviar", variant="primary", scale=1)
    
    with gr.Row():
        clear = gr.ClearButton([msg, chatbot], value="Limpiar chat")

    # Acción al enviar
    msg.submit(chat_interface, [msg, chatbot], [chatbot])
    msg.submit(lambda: "", None, msg) # Limpiar el input después de enviar
    
    submit_btn.click(chat_interface, [msg, chatbot], [chatbot])
    submit_btn.click(lambda: "", None, msg)

if __name__ == "__main__":
    demo.launch()
