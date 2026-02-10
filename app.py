import gradio as gr
from groq import Groq
import os

# 1. INICIALIZACIÓN DE JARVIS
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_v12_engine(mensaje, historial):
    # INSTRUCCIONES DE SISTEMA
    sistema = """Eres ADIA v1.2, la IA de ingeniería de Jorge. 
    Tu especialidad es el diseño de brazos robóticos y sistemas Stark.
    Uso real: Ayudas a calcular el torque de los motores, eliges los materiales y generas el código de control.
    Responde con datos técnicos, pero con la actitud de Jarvis: eficiente y protectora."""
    
    # --- ARREGLO PARA EL ERROR DE LA FOTO ---
    # Limpiamos el historial para que Groq reciba exactamente lo que pide
    mensajes_limpios = [{"role": "system", "content": sistema}]
    
    if historial:
        for chat in historial:
            if chat[0]: # Mensaje del usuario
                mensajes_limpios.append({"role": "user", "content": str(chat[0])})
            if chat[1]: # Mensaje de la IA
                mensajes_limpios.append({"role": "assistant", "content": str(chat[1])})
    
    # Añadir mensaje actual
    mensajes_limpios.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_limpios,
            temperature=0.4
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ FALLO EN MATRIZ DE DATOS: {str(e)}"

# 2. INTERFAZ DE LABORATORIO
with gr.Blocks(theme=gr.themes.Monochrome()) as app:
    gr.Markdown("# 🛡️ ADIA v1.2 | MECHANICAL DESIGN CORE")
    gr.Markdown("---")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="HUD de Ingeniería", height=500)
            with gr.Row():
                msg = gr.Textbox(placeholder="Ej: ADIA, calcula el torque para levantar 200g a 15cm...", scale=4)
                btn = gr.Button("ESCANEAR", variant="primary", scale=1)
        
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ ESPECIFICACIONES")
            gr.Label("SISTEMA: ESTABLE", label="Status")
            gr.Markdown("---")
            gr.Markdown("#### 🏗️ BLUEPRINTS")
            gr.Button("📄 Generar Plano 2D")
            gr.Button("💾 Exportar Código Arduino")
            gr.HTML("""
                <div style='background: #111; padding: 10px; border-radius: 5px; border: 1px solid #00f2ff;'>
                    <p style='color: #00f2ff; font-family: monospace; font-size: 10px;'>
                    >> PROTOCOLO: JARVIS ACTIVO<br>
                    >> ERROR FIX: FORMAT_OK<br>
                    >> NÚCLEO: LLAMA-3.3
                    </p>
                </div>
            """)

    # Lógica de envío
    def responder(m, h):
        if not m: return "", h
        res = adia_v12_engine(m, h)
        h.append((m, res))
        return "", h

    msg.submit(responder, [msg, chatbot], [msg, chatbot])
    btn.click(responder, [msg, chatbot], [msg, chatbot])

# 3. LANZAMIENTO (Ajustado para Render)
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=10000)
    
