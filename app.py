import os
import gradio as gr
from groq import Groq

# 1. Configuración del Cliente
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: No configuraste la variable GROQ_API_KEY en Render."

    system_prompt = (
        "Eres ADIA, la ayudante y compañera de Jorge el sera tu único usuario cuando te escriba debes contestarle con respeto y amabilidad. "
        "Tu objetivo es asistir en tareas y preguntas. "
        "Eres técnica, eficiente y siempre llamas a Jorge por su nombre."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # 2. LIMPIEZA DE MEMORIA (Extrayendo solo el texto puro)
    for entrada in historial:
        if isinstance(entrada, dict):
            rol = entrada.get("role")
            contenido = entrada.get("content")
            # Si el contenido es una lista/dict (como el error que viste), extraemos solo el texto
            if isinstance(contenido, list) and len(contenido) > 0:
                contenido = contenido[0].get("text", str(contenido))
            elif isinstance(contenido, dict):
                contenido = contenido.get("text", str(contenido))
                
            if rol and contenido:
                mensajes_api.append({"role": rol, "content": str(contenido)})
        elif isinstance(entrada, (list, tuple)) and len(entrada) == 2:
            u, b = entrada
            # Limpieza extra para el formato de lista antiguo
            if isinstance(u, dict): u = u.get("text", str(u))
            if isinstance(b, dict): b = b.get("text", str(b))
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7,
            max_tokens=1024
        )
        # 3. EXTRAER TEXTO LIMPIO DE LA RESPUESTA
        respuesta = completion.choices[0].message.content
        return respuesta
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA - IA")
    chat = gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)
