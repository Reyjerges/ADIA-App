import gradio as gr
from groq import Groq
import os

# Conexión con el cerebro de ADIA
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_logic(mensaje, historial):
    sistema = "Eres ADIA v1.2, asistente de Jorge. Eres experta en robótica. Saluda a Jorge si es el inicio. Si pide mover el brazo, responde confirmando la trayectoria."
    
    mensajes_ia = [{"role": "system", "content": sistema}]
    for h in historial:
        mensajes_ia.append({"role": "user", "content": h[0]})
        mensajes_ia.append({"role": "assistant", "content": h[1]})
    mensajes_ia.append({"role": "user", "content": mensaje})

    response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=mensajes_ia)
    return response.choices[0].message.content

# --- HTML/CSS PARA EL BRAZO ROBÓTICO (SIMULACIÓN) ---
brazo_3d_html = """
<div style="width: 100%; height: 400px; background: #0a0a0a; border: 2px solid #00f2ff; border-radius: 10px; overflow: hidden; position: relative;">
    <div style="position: absolute; top: 10px; left: 10px; color: #00f2ff; font-family: monospace; font-size: 12px;">ADIA_VISUAL_FEED: ACTIVE</div>
    <svg viewBox="0 0 200 200" style="width: 100%; height: 100%;">
        <rect x="80" y="160" width="40" height="20" fill="#333" />
        <g id="robot-arm">
            <rect x="95" y="100" width="10" height="60" fill="#00f2ff">
                <animateTransform attributeName="transform" type="rotate" from="0 100 160" to="20 100 160" dur="2s" repeatCount="indefinite" />
            </rect>
            <circle cx="100" cy="100" r="5" fill="white" />
        </g>
    </svg>
</div>
"""

# --- CONSTRUCCIÓN DE LA INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft()) as interface:
    gr.Markdown("## 🦾 ADIA v1.2 // Jorge's Lab")
    
    # TELEMETRÍA SUPERIOR
    with gr.Row():
        gr.HTML("<div style='width:100%; height:20px; background:linear-gradient(90deg, #00f2ff 30%, #333 30%); border-radius:5px;'></div>")

    with gr.Row():
        # IZQUIERDA: ADIA CHAT
        with gr.Column(scale=1):
            chat = gr.Chatbot(label="Terminal", height=450)
            txt = gr.Textbox(show_label=False, placeholder="Envía un comando a ADIA...")
            btn_canvas = gr.Button("🚀 ACTIVAR CANVAS", variant="primary")

        # DERECHA: CANVAS (Oculto hasta que presiones el botón)
        with gr.Column(scale=1, visible=False) as canvas_area:
            gr.Markdown("### 🖥️ SIMULADOR DE BRAZO")
            gr.HTML(brazo_3d_html)
            gr.Markdown("#### 📊 TELEMETRÍA DE MOTORES")
            gr.HTML("<div style='color:#00f2ff; font-family:monospace;'>MOTOR_A: 45° | MOTOR_B: 12° | TEMP: 32°C</div>")

    # FUNCIONES
    def activar():
        return gr.update(visible=True)

    def responder(m, h):
        res = adia_logic(m, h)
        h.append((m, res))
        return "", h

    # EVENTOS
    txt.submit(responder, [txt, chat], [txt, chat])
    btn_canvas.click(activar, None, canvas_area)

interface.launch()
