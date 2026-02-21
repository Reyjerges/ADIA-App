\import os
import gradio as gr
from groq import Groq

# 1. Configuración Limpia
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def responder_adia(mensaje, historial):
    if not api_key: return "Jorge, falta la API KEY."

    # PROMPT DE HIERRO: Instrucciones estrictas para que no hable raro
    system_prompt = (
        "Eres ADIA, la compañera técnica de Jorge. Tu tono es profesional, "
        "directo y eficiente. NUNCA uses palabras cariñosas ni románticas. "
        "Llama a Jorge por su nombre. Tu objetivo es ayudarlo a programar y charlar con lógica."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # 2. FILTRO ANTI-ERRORES: Limpiamos el historial de cualquier metadato de Gradio
    for h in historial[-4:]:
        # Gradio 5 puede enviar listas [user, bot] o diccionarios
        user_content = ""
        bot_content = ""
        
        if isinstance(h, (list, tuple)):
            user_content = str(h[0]) if h[0] else ""
            bot_content = str(h[1]) if h[1] else ""
        elif isinstance(h, dict):
            user_content = str(h.get("content", ""))
            
        if user_content: mensajes_api.append({"role": "user", "content": user_content})
        if bot_content: mensajes_api.append({"role": "assistant", "content": bot_content})

    # Mensaje actual limpio
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        # Usamos Mixtral para que no se bloquee como el 70B
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768", 
            messages=mensajes_api,
            temperature=0.5, # Bajamos la temperatura para que sea más seria y no invente cosas
            max_tokens=800
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Jorge, el sistema dio un error técnico: {str(e)}"

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Default()) as demo:
    gr.Markdown("# 🤖 ADIA")
    gr.ChatInterface(fn=responder_adia)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
