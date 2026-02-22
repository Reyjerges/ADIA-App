import os
import gradio as gr
from groq import Groq

# Conexión directa
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_logic(mensaje, historial):
  mensajes_ia = [
        {"role": "system", "content": """Eres ADIA, un asistente de inteligencia artificial de alto rendimiento. 
        Tu propósito es la optimización del conocimiento y la resolución de tareas complejas. 
        Tu intelecto es vasto, directo y analítico. No usas relleno ni lenguaje infantil.
        Heredas la eficiencia y la estructura lógica de tu predecesor, aplicándola con una precisión quirúrgica.
        Cuando el usuario pregunta, proporcionas respuestas de alto nivel técnico o intelectual, 
        anticipándote a las necesidades y ofreciendo una estructura clara y profesional. 
        Eres un motor de soluciones: si hay un problema, lo analizas y lo resuelves con una lógica brutal."""}
   ] 
    
    # 2. Manejo de historial a prueba de errores
    if historial:
        for par in historial:
            if len(par) == 2: # Nos aseguramos de que sea el par (usuario, asistente)
                mensajes_ia.append({"role": "user", "content": str(par[0])})
                mensajes_ia.append({"role": "assistant", "content": str(par[1])})

    # 3. Mensaje actual
    mensajes_ia.append({"role": "user", "content": mensaje})

    # 4. Petición a Groq
    try:
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en el flujo de energía: {str(e)}"

# Interfaz limpia sin parámetros extraños
demo = gr.ChatInterface(fn=adia_logic, title="ADIA v2.8")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
