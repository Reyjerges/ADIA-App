import gradio as gr
from groq import Groq
import os

# 1. CONFIGURACIÓN
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_brain(mensaje, historial):
    sistema = "Eres ADIA v1.2, asistente de Jorge. Eres experta en robótica."
    mensajes_limpios = [{"role": "system", "content": sistema}]
    
    if historial:
        for par in historial:
            if par[0]: mensajes_limpios.append({"role": "user", "content": str(par[0])})
            if par[1]: mensajes_limpios.append({"role": "assistant", "content": str(par[1])})
    
    mensajes_limpios.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=mensajes_limpios)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# 2. HTML Y JS (El bloque que causaba el error de comillas)
vision_pro_html = """
<div style="display: flex; flex-direction: column; align-items: center; background: #050505; padding: 10px; border-radius: 10px; border: 2px solid #00f2ff;">
    <video id="webcam" style="width: 100%; max-width: 400px; border-radius: 5px; transform: scaleX(-1);" autoplay playsinline></video>
    <canvas id="output_canvas" style="position: absolute; width: 100%; max-width: 400px; transform: scaleX(-1);"></canvas>
    <div id="status" style="color: #00f2ff; font-family: monospace; margin-top: 10px;">[ BUSCANDO MANO ]</div>
    <svg viewBox="0 0 200 200" style="width: 150px; height: 150px;">
        <line id="robot_line" x1="100" y1="180" x2="100" y2="100" stroke="#00f2ff" stroke-width="8" stroke-linecap="round" />
        <circle id="joint" cx="100" cy="100" r="6" fill="white" />
    </svg>
</div>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
<script>
const video = document.getElementById('webcam');
const arm = document.getElementById('robot_line');
const joint = document.getElementById('joint');
const hands = new Hands({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`});
hands.setOptions({maxNumHands: 1, modelComplexity: 1, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5});
hands.onResults((results) => {
  if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
    const p = results.multiHandLandmarks[0][8];
    const tx = 100 + (p.x - 0.5) * 100;
    const ty = 180 - (1 - p.y) * 150;
    arm.setAttribute('x2', tx); arm.setAttribute('y2', ty);
    joint.setAttribute('cx', tx); joint.setAttribute('cy', ty);
    document.getElementById('status').innerText = "[ MANO DETECTADA ]";
  }
});
new Camera(video, {onFrame: async () => await hands.send({image: video}), width: 640, height: 480}).start();
</script>
"""

# 3. INTERFAZ
with gr.Blocks(theme=gr.themes.Monochrome()) as app:
    gr.Markdown("# 🦾 ADIA v1.2")
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot(height=400)
            msg = gr.Textbox(label="Comando")
            btn = gr.Button("🚀 ACTIVAR CANVAS")
        with gr.Column(visible=False) as canvas_col:
            gr.HTML(vision_pro_html)

    def responder(m, h):
        res = adia_brain(m, h)
        h.append((m, res))
        return "", h

    msg.submit(responder, [msg, chatbot], [msg, chatbot])
    btn.click(lambda: gr.update(visible=True), None, canvas_col)

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=10000)
