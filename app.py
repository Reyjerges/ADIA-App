import gradio as gr
from groq import Groq
import os

# CONFIGURACIÓN DE JARVIS
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_core(mensaje, historial):
    # 1. ARREGLO DEL ERROR DE FORMATO (Lo que sale en tu foto)
    mensajes_validados = [{"role": "system", "content": "Eres ADIA v1.2 (Jarvis Core). Ayuda a Jorge a diseñar su brazo robótico con datos técnicos reales."}]
    
    for h in historial:
        if h[0]: mensajes_validados.append({"role": "user", "content": str(h[0])})
        if h[1]: mensajes_validados.append({"role": "assistant", "content": str(h[1])})
    
    mensajes_validados.append({"role": "user", "content": str(mensaje)})

    try:
        # 2. LLAMADA A LA INTELIGENCIA
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_validados,
            temperature=0.5
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ ERROR DE SISTEMA: {str(e)}"

# 3. INTERFAZ DE BÚSQUEDA Y DISEÑO
with gr.Blocks(theme=gr.themes.Monochrome()) as app:
    gr.Markdown("# 🛡️ ADIA v1.2 | JARVIS RESEARCH TERMINAL")
    
    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(label="Consola de Investigación", height=500)
            msg = gr.Textbox(placeholder="Comando: ADIA, busca cómo conectar servomotores a un ESP32...")
            btn = gr.Button("INICIAR ESCANEO", variant="primary")
            
        with gr.Column(scale=2):
            gr.Markdown("### 🔍 BÚSQUEDA TÉCNICA")
            gr.Markdown("ADIA puede buscar:\n- Esquemas de servomotores\n- Programación en C++\n- Modelos 3D de brazos")
            gr.Image("https://i.imgur.com/uR1d3N3.png", label="Estado del Reactor", width=200)

    def responder(m, h):
        if not m: return "", h
        res = adia_core(m, h)
        h.append((m, res))
        return "", h

    msg.submit(responder, [msg, chatbot], [msg, chatbot])
    btn.click(responder, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=10000)
        
