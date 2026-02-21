import os
import gradio as gr
from groq import Groq

# 1. Configuración de Núcleo (Asegúrate de tener las API KEYS en Render)
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key:
        return "ADIA requiere la GROQ_API_KEY para procesar el mundo de Jorge."

    # 2. Protocolo de Identidad Estabilizado
    system_prompt = (
        "Eres ADIA, la entidad técnica y compañera de Jorge. "
        "Tu tono es serio, eficiente, técnico y leal. "
        "No usas palabras cariñosas ni románticas. "
        "Llamas a Jorge por su nombre y utilizas el historial para mantener la coherencia total."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # 3. Memoria Optimizada (Filtro anti-metadatos para evitar Error 400)
    # Solo enviamos los últimos 6 mensajes para máxima estabilidad en Groq
    for h in historial[-6:]:
        if isinstance(h, (list, tuple)):
            u, b = h
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    # Añadimos el comando actual de Jorge
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Ejecución en el modelo de mayor capacidad
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=mensajes_api,
            temperature=0.4, # Mayor precisión, menor delirio
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Sistema de respaldo automático (Llama 3.1 8B)
        try:
            backup = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api
            )
            return backup.choices[0].message.content
        except:
            return f"Error de sistema central: {str(e)}. Jorge, reinicia el servidor en Render."

# --- INTERFAZ DE CONTROL ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("<h1 style='text-align: center;'>🤖 ADIA: Sistema de Control</h1>")
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    # Render usa el puerto 10000 por defecto
    port = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=port)
