import gradio as gr
from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_brain(mensaje, historial):
    sistema = "Eres ADIA v1.2, asistente de Jorge. Eres experta en robótica y visión espacial. Saluda a Jorge y confirma que el rastreo de manos está activo."
    mensajes = [{"role": "system", "content": sistema}]
    for h in historial:
        mensajes.append({"role": "user", "content": h[0]})
        mensajes.append({"role": "assistant", "content": h[1]})
    mensajes.append({"role": "user", "content": mensaje})
    
    completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=mensajes)
    return completion.choices[0].message.content

# --- EL MOTOR VISION PRO (JavaScript + HTML) ---
vision_pro_html = """
<div style="display: flex; flex-direction: column; align-items: center; background: #050505; padding: 15px; border-radius: 15px; border: 2px solid #00f2ff;">
    <div style="position: relative; width: 100%; max-width: 400px;">
        <video id="webcam" style="width: 100%; border-radius: 10px; transform: scaleX(-1);" autoplay playsinline></video>
        <canvas id="output_canvas" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; transform: scaleX(-1);"></canvas>
    </div>
    <div id="status" style="color: #00f2ff; font-family: monospace; margin-top: 10px; font-size: 14px;">SISTEMA GESTUAL: ESPERANDO MANO...</div>
    
    <svg viewBox="0 0 200 200" style="width: 200px; height: 200px; margin-top: 20px;">
        <rect x="90" y="180" width="20" height="10" fill="#333" />
        <g id="arm_visual">
            <line id="robot_line" x1="100" y1="180" x2="100" y2="80" stroke="#00f2ff" stroke-width="8" stroke-linecap="round" />
            <circle id="joint" cx="100" cy="80" r="6" fill="#fff" />
        </g>
    </svg>
</div>

<script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js"></script>

<script>
const video = document.getElementById('webcam');
const canvasElement = document.getElementById('output_canvas');
const canvasCtx = canvasElement.getContext('2d');
const arm = document.getElementById('robot_line');
const joint = document.getElementById('joint');
const status = document.getElementById('status');

function onResults(results) {
  canvasCtx.save();
  canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
  
  if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
    status.innerText = "SISTEMA GESTUAL: MANO DETECTADA";
    status.style.color = "#00ff00";
    
    const landmarks = results.multiHandLandmarks[0];
    // Punto 8 es la punta del dedo índice
    const indexY = landmarks[8].y * 100; 
    
    // Mover el brazo visual basado en el dedo
    const newY = 180 - ( (1 - landmarks[8].y) * 150 );
    arm.setAttribute('x2', 100 + (landmarks[8].x - 0.5) * 100);
    arm.setAttribute('y2', newY);
    joint.setAttribute('cx', 100 + (landmarks[8].x - 0.5) * 100);
    joint.setAttribute('cy', newY);

    drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {color: '#00f2ff', lineWidth: 2});
    drawLandmarks(canvasCtx, landmarks, {color: '#ffffff', lineWidth: 1, radius: 2});
  } else {
    status.innerText = "SISTEMA GESTUAL: BUSCANDO MANO...";
    status.style.color = "#ff0055";
  }
  canvasCtx.restore();
}

const hands = new Hands({locateFile: (file) => {
  return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
}});

hands.setOptions({
  maxNumHands: 1,
  modelComplexity: 1,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5
});
hands.onResults(onResults);

const camera = new Camera(video, {
  onFrame: async () => {
    await hands.send({image: video});
  },
  width: 640,
  height: 480
});
camera.start();
</script>
"""

# --- INTERFAZ GRADIO ---
with gr.Blocks(theme=gr.themes.Monochrome()) as app:
    gr.Markdown("# 🦾 ADIA v1.2 | VISION PRO MODE")
    
    with gr.Row():
        # IZQUIERDA: CHAT
        with gr.Column(scale=1):
            chatbot = gr.Chatbot(label="ADIA Terminal", height=400)
            msg = gr.Textbox(placeholder="Pregunta a ADIA o pide control total...")
            btn_canvas = gr.Button("🚀 ACTIVAR MODO GESTUAL (CANVAS)", variant="primary")

        # DERECHA: EL CANVAS CON CÁMARA
        with gr.Column(scale=1, visible=False) as canvas_col:
            gr.Markdown("### 👁️ EYE-TRACKING & GESTURE ENGINE")
            gr.HTML(vision_pro_html)
            gr.Markdown("---")
            gr.Markdown("#### 📈 TELEMETRÍA ESPACIAL")
            gr.HTML("<div style='font-family:monospace; color:lime;'>X-AXIS: ACTIVE | Y-AXIS: ACTIVE | Z-DEPTH: CALIBRATING...</div>")

    # LÓGICA
    def toggle_canvas():
        return gr.update(visible=True)

    def response(m, h):
        res = adia_brain(m, h)
        h.append((m, res))
        return "", h

    msg.submit(response, [msg, chatbot], [msg, chatbot])
    btn_canvas.click(toggle_canvas, None, canvas_col)

app.launch()
