import os
import gradio as gr
from groq import Groq

# Configuración del Cliente
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

def adia_chat(mensaje, historial):
    # System Prompt: La esencia de ADIA
    mensajes_ia = [
        {"role": "system", "content": "Eres ADIA. Inteligencia de alto nivel, directa y eficiente. Tienes memoria de esta charla con Jorge."}
    ]
    
    # Procesamiento del historial ultra-seguro
    if historial:
        for h in historial:
            try:
                # Intentamos extraer usuario y asistente
                user_part = h[0] if len(h) > 0 else ""
                bot_part = h[1] if len(h) > 1 else ""
                if user_part: mensajes_ia.append({"role": "user", "content": user_part})
                if bot_part: mensajes_ia.append({"role": "assistant", "content": bot_part})
            except:
                continue # Si falla una línea del historial, saltamos a la siguiente
    
    # Mensaje actual
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # Usamos el modelo 8b que es más rápido y menos propenso a errores de cuota
        completion = client.chat.completions.create(
            messages=mensajes_ia,
            model="llama-3.1-8b-instant", 
            temperature=0.5
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en la conexión de ADIA: {str(e)}"

# Interfaz
demo = gr.ChatInterface(fn=adia_chat, title="ADIA")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
