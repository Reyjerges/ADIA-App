import os
import gradio as gr
from groq import Groq

# Configuración del Cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def responder_adia(mensaje, historial):
    system_prompt = "Eres ADIA, una IA experta en física y robótica creada para ser una asistente y compañera."
    
    # Construimos los mensajes desde cero para que Groq no se confunda
    mensajes_redactados = [{"role": "system", "content": system_prompt}]
    
    # Agregamos el historial solo si tiene contenido válido
    for chat in historial:
        if len(chat) == 2:
            user_msg, bot_msg = chat
            if user_msg:
                mensajes_redactados.append({"role": "user", "content": str(user_msg)})
            if bot_msg:
                mensajes_redactados.append({"role": "assistant", "content": str(bot_msg)})
    
    # Mensaje actual
    mensajes_redactados.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_redactados,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Esto imprimirá el error real en los logs de Render para que lo veamos
        print(f"ERROR CRÍTICO: {e}")
        return "ADIA: Tuve un error de memoria. Intenta refrescar la página."

# Interfaz básica (simplificada para evitar errores de Gradio)
demo = gr.ChatInterface(fn=responder_adia, title="ADIA v2.0")

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
