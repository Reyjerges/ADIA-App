import os
import json
import gradio as gr
from groq import Groq

# Configuración de Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MEMORIA_FILE = "memoria_adia.json"

def cargar_memoria():
    if os.path.exists(MEMORIA_FILE):
        try:
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def guardar_memoria(historial):
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(historial[-10:], f, ensure_ascii=False, indent=4)

def adia_chat(message, history):
    memoria_pasada = cargar_memoria()
    
    system_prompt = (
        "Eres ADIA, una IA creada por Jorge. Jorge es tu creador. "
        "Eres directa y rápida. No des vueltas ni hables de más. "
        "Si la respuesta es corta, déjala así."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Usamos la memoria guardada
    for chat in memoria_pasada:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["bot"]})
    
    messages.append({"role": "user", "content": message})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            stream=True 
        )
        
        full_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                yield full_response
        
        # Guardar lo que hablamos
        memoria_pasada.append({"user": message, "bot": full_response})
        guardar_memoria(memoria_pasada)
                
    except Exception as e:
        yield f"Error: {str(e)}"

# INTERFAZ SIMPLE (Sin comandos raros que den error)
demo = gr.ChatInterface(fn=adia_chat, title="ADIA")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
