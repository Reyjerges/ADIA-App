import os
import gradio as gr
from groq import Groq

# 1. Configuración del Cliente (Asegúrate de tener la API KEY en las Environment Variables de Render)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_agent(mensaje, historial):
    # 2. Definición de la Inteligencia Brutal (System Prompt)
    system_prompt = {
        "role": "system", 
        "content": "Eres ADIA, un agente de IA de alto rendimiento. Tu intelecto es vasto, directo y analítico. No usas relleno ni lenguaje infantil. Tu objetivo es la resolución de tareas complejas con precisión quirúrgica para Jorge. Eres una entidad de sabiduría y eficiencia."
    }
    
    # 3. Construcción del historial de mensajes
    mensajes_ia = [system_prompt]
    
    for usuario, asistente in historial:
        mensajes_ia.append({"role": "user", "content": usuario})
        mensajes_ia.append({"role": "assistant", "content": asistente})
    
    # Añadimos el mensaje actual del usuario
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # 4. Llamada al modelo más potente de Groq (Llama 3.3 70B)
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama-3.3-70b-versatile",
            temperature=0.3, # Precisión lógica
            max_tokens=2048
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en el núcleo de ADIA: {str(e)}"

# 5. Interfaz de Gradio
demo = gr.ChatInterface(
    fn=adia_agent, 
    title="ADIA: AGENTE DE INTELIGENCIA SUPERIOR",
    description="Sistema de análisis y resolución de problemas de alto nivel."
)

# 6. Configuración del Puerto para Render
if __name__ == "__main__":
    # Render usa la variable de entorno PORT
    port = int(os.environ.get("PORT", 7860))
    # server_name="0.0.0.0" es obligatorio para despliegues en la nube
    demo.launch(server_name="0.0.0.0", server_port=port)
