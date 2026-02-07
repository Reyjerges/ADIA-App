import os
import gradio as gr
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # --- INSTRUCCIONES DE IDENTIDAD Y MEMORIA ---
    instrucciones = (
        "Eres ADIA (Advanced Digital Intelligence Architecture),. "
        "Tu nombre también significa 'Vida/Existencia'. Creada por Jorge. "
        "MEMORIA ACTIVA: Debes prestar mucha atención al historial de nuestra conversación. "
        "Si Jorge te pregunta algo sobre un tema anterior (como una ballena o un motor), "
        "revisa los mensajes previos para dar una respuesta coherente. "
        "\n\nMODULO DE IMAGEN: Si pide un dibujo, usa: "
        "![imagen](https://pollinations.ai/p/PROMPT?width=1080&height=1080&nologo=true) "
        "(Traduce PROMPT al inglés)."
    )
    
    # Iniciamos la lista de mensajes con el sistema
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # PASO CLAVE: Construimos la memoria real pasando par a par el historial
    for usuario, asistente in historial:
        mensajes.append({"role": "user", "content": usuario})
        mensajes.append({"role": "assistant", "content": asistente})
    
    # Añadimos la pregunta actual de Jorge
    mensajes.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.7 # Bajamos un poco la temperatura para que sea más precisa con la memoria
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en los circuitos de memoria: {str(e)}"

# Interfaz con tema oscuro profesional
demo = gr.ChatInterface(
    fn=chat_adia, 
    title="ADIA v2.0",
    description="Arquitectura de Inteligencia Digital Avanzada | Memoria y Arte Activos",
    theme="monochrome" # Estilo más brutal y serio
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
