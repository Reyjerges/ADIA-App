import os
import gradio as gr
from groq import Groq

# 1. Configuración
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # Forzamos la personalidad en cada interacción
    identidad = (
        "Eres ADIA, la IA personal de Jorge. Habla de forma natural, "
        "amistosa y técnica cuando sea necesario. No seas un robot genérico."
    )
    
    mensajes_limpios = [{"role": "system", "content": identidad}]
    
    # 2. Limpieza profunda del historial
    for h in historial:
        # Extraemos el contenido sin importar el formato raro de Gradio
        if isinstance(h, dict):
            contenido = h.get("content", "")
            # Si el contenido es una lista/dict (como el que viste), extraemos el texto
            if isinstance(contenido, list) and len(contenido) > 0:
                contenido = contenido[0].get("text", "")
            
            mensajes_limpios.append({
                "role": h.get("role", "user"),
                "content": str(contenido)
            })
        elif isinstance(h, (list, tuple)):
            mensajes_limpios.append({"role": "user", "content": str(h[0])})
            mensajes_limpios.append({"role": "assistant", "content": str(h[1])})

    mensajes_limpios.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_limpios,
            temperature=0.8
        )
        # 3. Retornamos SOLO el texto plano
        respuesta = completion.choices[0].message.content
        return respuesta
    except Exception as e:
        return f"Error: {str(e)}"

# 4. Interfaz simplificada para evitar metadatos
demo = gr.ChatInterface(
    fn=chat_adia,
    title="ADIA",
    type="messages" # Forzamos el nuevo formato de Gradio para controlarlo mejor
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
    
