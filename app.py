import os
import gradio as gr
from groq import Groq

# 1. Configuración de Poder
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key:
        return "Jorge, la cámara de regeneración (API KEY) no está lista en Render."

    # Prompt de identidad: ADIA sabe quién eres y cuál es su propósito
    system_prompt = (
        "Eres ADIA, la compañera de Jorge. Tu personalidad es técnica, directa, "
        "inteligente y leal. Siempre te diriges a Jorge por su nombre. "
        "Hablas con claridad y ayudas en proyectos como Godot y desarrollo de juegos."
    )
    
    # 2. MEMORIA PERFECTA: Formateo dinámico para evitar errores de Gradio
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # Solo tomamos los últimos 5 intercambios para mantener la estabilidad total
    for h in historial[-5:]:
        if isinstance(h, (list, tuple)):
            user_part, assistant_part = h
            if user_part: mensajes_api.append({"role": "user", "content": str(user_part)})
            if assistant_part: mensajes_api.append({"role": "assistant", "content": str(assistant_part)})
        elif isinstance(h, dict):
            mensajes_api.append(h)

    # Añadimos el mensaje actual de Jorge
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Modelo Mixtral: Potencia sin los bloqueos del 70B
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768", 
            messages=mensajes_api,
            temperature=0.6,
            max_tokens=1500
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Sistema de seguridad: si Mixtral falla, el 8B entra de inmediato
        try:
            backup = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api
            )
            return backup.choices[0].message.content
        except:
            return f"Jorge, el sistema está bajo mucha presión. Error: {str(e)}"

# --- INTERFAZ NIVEL PERFECCIÓN ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("<h1 style='text-align: center;'>🤖 ADIA</h1>")
    gr.Markdown("<p style='text-align: center;'>Compañera de Jorge | Estado: <b>Perfecto</b></p>")
    
    # Gradio 5+ detecta automáticamente el historial aquí
    gr.ChatInterface(
        fn=responder_adia,
        examples=["Jorge, ¿listo para trabajar en Godot?", "Explícame el código de Zylann"],
        cache_examples=False
    )

if __name__ == "__main__":
    # Render usa el puerto 10000 o 7860 según configuración
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)
