import os
import gradio as gr
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_agent(mensaje, historial):
    # Definición del Sistema (Personalidad de Inteligencia Brutal)
    system_prompt = {
        "role": "system", 
        "content": "Eres ADIA, un agente de IA de alto rendimiento. Tu enfoque es la lógica pura, la eficiencia y la resolución de problemas complejos. No usas relleno."
    }
    
    # Construcción de la lista de mensajes
    # Aquí es donde solía estar el error del corchete ]
    mensajes_ia = [system_prompt]
    
    for usuario, asistente in historial:
        mensajes_ia.append({"role": "user", "content": usuario})
        mensajes_ia.append({"role": "assistant", "content": asistente})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama-3.1-8b-instant",
            temperature=0.3, # Menor temperatura = más precisión lógica
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en el núcleo del agente: {str(e)}"

# Interfaz
demo = gr.ChatInterface(fn=adia_agent, title="ADIA AGENT v1.0")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
