import os
import gradio as gr
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_logic(mensaje, historial):
    # 1. Definimos el sistema con personalidad
    mensajes_ia = [
        {"role": "system", "content": "Eres ADIA, una IA experta en Anime (JJK, DB) y tecnología. Tu personalidad es épica y profesional. ¡No respondas con mensajes cortos y aburridos!"}
    ]
    
    # 2. Arreglo del ValueError: Manejamos el historial correctamente
    if historial:
        for chat in historial:
            # Gradio a veces manda diccionarios o listas, esto lo asegura:
            if isinstance(chat, dict):
                mensajes_ia.append({"role": "user", "content": chat["human"]})
                mensajes_ia.append({"role": "assistant", "content": chat["ai"]})
            else:
                user_part, assistant_part = chat
                mensajes_ia.append({"role": "user", "content": user_part})
                mensajes_ia.append({"role": "assistant", "content": assistant_part})

    # 3. Añadimos el mensaje actual
    mensajes_ia.append({"role": "user", "content": mensaje})

    # 4. Petición a Groq
    try:
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama-3.1-8b-instant",
            temperature=0.8, # Más personalidad
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error de Ki: {str(e)}"

# Interfaz con estilo
demo = gr.ChatInterface(
    fn=adia_logic, 
    title="ADIA v2.7",
    description="¡El retorno del Guerrero! Ahora sin errores de memoria.",
    type="messages" # Esto ayuda a evitar el error de 'unpack' en versiones nuevas de Gradio
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
