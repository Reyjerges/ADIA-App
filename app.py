import os
import gradio as gr
from groq import Groq

# 1. Configuración del Cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # Instrucciones de identidad (Ancla)
    instrucciones = (
        "Eres ADIA, la IA de Jorge. Habla de forma natural y cercana. "
        "No eres un asistente genérico, eres su compañera técnica y creativa."
    )
    
    mensajes_para_groq = [{"role": "system", "content": instrucciones}]
    
    # 2. LIMPIEZA TOTAL DEL HISTORIAL (Evita que ADIA vea metadatos o códigos)
    for h in historial:
        # Si Gradio envía diccionarios (Gradio 5)
        if isinstance(h, dict):
            rol = h.get("role", "user")
            contenido = h.get("content", "")
            # Si el contenido es esa lista rara de Gradio, extraemos solo el texto
            if isinstance(contenido, list) and len(contenido) > 0:
                contenido = contenido[0].get("text", "")
            
            if rol and contenido:
                mensajes_para_groq.append({"role": rol, "content": str(contenido)})
        
        # Si Gradio envía listas (Gradio antiguo)
        elif isinstance(h, (list, tuple)) and len(h) == 2:
            if h[0]: mensajes_para_groq.append({"role": "user", "content": str(h[0])})
            if h[1]: mensajes_para_groq.append({"role": "assistant", "content": str(h[1])})

    # Mensaje actual
    mensajes_para_groq.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_para_groq,
            temperature=0.8
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# 3. Interfaz sin parámetros conflictivos
demo = gr.ChatInterface(
    fn=chat_adia, 
    title="ADIA"
)

if __name__ == "__main__":
    # Configuración obligatoria para Render
    demo.launch(server_name="0.0.0.0", server_port=10000)
  
