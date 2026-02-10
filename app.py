import gradio as gr
from groq import Groq
import os

# Configuración de la API Key
# Asegúrate de tener la variable de entorno GROQ_API_KEY configurada
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def adia_chat_response(message, history):
    """
    Función para procesar los mensajes del chat usando el modelo Llama 3.1 de Groq.
    Mantiene el historial de la conversación para dar contexto.
    """
    try:
        if not api_key:
            return "❌ Error: La API Key de Groq no está configurada. Por favor, revisa tus variables de entorno."
        
        # Mensaje de sistema para definir la personalidad de ADIA
        messages = [{"role": "system", "content": "Eres ADIA, una IA avanzada, brillante y muy comunicativa. Respondes de forma clara, amable y profesional."}]
        
        # Reconstrucción del historial de la conversación
        for turn in history:
            if isinstance(turn, dict):
                role = turn.get("role")
                content = turn.get("content")
                if role and content:
                    messages.append({"role": role, "content": content})
            elif isinstance(turn, (list, tuple)) and len(turn) == 2:
                # Formato estándar de Gradio ChatInterface (Usuario, Asistente)
                messages.append({"role": "user", "content": turn[0]})
                messages.append({"role": "assistant", "content": turn[1]})
        
        # Añadir el mensaje actual del usuario
        messages.append({"role": "user", "content": message})
        
        # Llamada a la API de Groq
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        return f"❌ Error del sistema: {str(e)}"

# Construcción de la Interfaz de Usuario con Gradio
with gr.Blocks(title="ADIA AI", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 ADIA: Intelligence Only
    ### Bienvenida al modo de conversación avanzada.
    """)
    
    # Interfaz de Chat optimizada
    gr.ChatInterface(
        fn=adia_chat_response,
        chatbot=gr.Chatbot(height=500, bubble_full_width=False),
        textbox=gr.Textbox(placeholder="Escribe tu mensaje aquí...", container=False, scale=7),
        examples=["Hola ADIA, ¿qué puedes hacer?", "¿Puedes explicarme la computación cuántica?", "Escríbeme un poema corto."],
        cache_examples=False,
    )

    gr.Markdown("---")
    gr.Markdown("ADIA funciona mediante la API de Groq y el modelo Llama 3.1.")

if __name__ == "__main__":
    # Obtener puerto de las variables de entorno para despliegue (ej. Render o Heroku)
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
