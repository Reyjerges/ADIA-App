import os
import gradio as gr
from groq import Groq

# Configuración del Cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_chat(mensaje, historial):
    # Personalidad: Inteligencia Brutal
    mensajes_ia = [
        {"role": "system", "content": "Eres ADIA. Una inteligencia de alto nivel, directa, analítica y sin rodeos. Tu objetivo es resolver lo que Jorge solicite con máxima eficiencia lógica."}
    ]
    
    # Procesamiento seguro del historial para evitar ValueError
    if historial:
        for interaccion in historial:
            if len(interaccion) == 2:
                user_msg, bot_msg = interaccion
                mensajes_ia.append({"role": "user", "content": user_msg})
                mensajes_ia.append({"role": "assistant", "content": bot_msg})
    
    # Mensaje actual
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama-3.3-70b-versatile",
            temperature=0.4
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Interfaz simplificada
demo = gr.ChatInterface(
    fn=adia_chat, 
    title="ADIA",
    description="Inteligencia pura."
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
