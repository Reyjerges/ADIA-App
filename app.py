import os
import gradio as gr
from groq import Groq

# 1. Configuración del Cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # Identidad básica sin instrucciones de imagen
    instrucciones = (
        "Eres ADIA, la IA personal de Jorge. "
        "Tu objetivo es ayudarle en todo lo que necesite. "
        "Mantén una conversación fluida y recuerda lo que habéis hablado."
    )
    
    # Lista de mensajes limpia
    mensajes_limpios = [{"role": "system", "content": instrucciones}]
    
    # 2. LIMPIEZA DE HISTORIAL (Para evitar el error de metadatos)
    for h in historial:
        if isinstance(h, dict):
            # Extraemos solo texto, ignorando metadatos de Gradio
            mensajes_limpios.append({
                "role": str(h.get("role")), 
                "content": str(h.get("content"))
            })
        elif isinstance(h, (list, tuple)):
            # Soporte para formato de lista [usuario, bot]
            mensajes_limpios.append({"role": "user", "content": str(h[0])})
            mensajes_limpios.append({"role": "assistant", "content": str(h[1])})
    
    # Mensaje actual
    mensajes_limpios.append({"role": "user", "content": str(mensaje)})

    try:
        # 3. Llamada a la API
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_limpios,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error técnico: {str(e)}"

# 4. Interfaz de Gradio
demo = gr.ChatInterface(
    fn=chat_adia, 
    title="ADIA: Chat Personal"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
