import gradio as gr
from groq import Groq
import os

# 1. CONFIGURACIÓN DEL CEREBRO
# Asegúrate de tener la variable GROQ_API_KEY en el panel de Render
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def adia_brain(mensaje, historial):
    sistema = "Eres ADIA v1.2, asistente de ingeniería de Jorge. Eres técnica y usas un tono estilo Jarvis/F.R.I.D.A.Y. Saluda a Jorge por su nombre si es el inicio. Confirma que el sistema de visión gestual está listo."
    
    # Formato correcto de mensajes para la API de Groq
    mensajes_ia = [{"role": "system", "content": sistema}]
    
    for h in historial:
        if h[0]: # Mensaje del usuario
            mensajes_ia.append({"role": "user", "content": h[0]})
        if h[1]: # Respuesta de ADIA
            mensajes_ia.append({"role": "assistant", "content": h[1]})
            
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_ia,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"ERROR DE SISTEMA: {str(e)}"

# 2. EL MOTOR DE VISIÓN (HTML + JAVASCRIPT)
vision_pro_html = """
<div style="display: flex; flex-direction: column; align-items: center; background: #050505; padding: 15px; border-radius: 15px; border: 2px solid #00f2ff; font-family: 'Courier New', Courier, monospace;">
    <div style="position: relative; width: 100%; max-width: 480px;">
        <video id="webcam" style="width: 100%; border-radius: 10px; transform: scaleX(-1); border: 1px solid #333;" autoplay playsinline></video>
        <canvas id="output_canvas" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; transform: scaleX(-1);"></canvas>
    </div>
    <div id="status" style="color: #00f2ff; margin-top: 10px; font-size: 14px; text-transform: uppercase; font-weight: bold;">[ SISTEMA GESTUAL: STANDBY ]</div>
    
    <svg viewBox="0 0 200 200" style="width: 200px; height: 200px; margin-top: 20px; filter: drop-shadow(0 0 5px #00f2ff);">
        <rect x="80" y="185" width="40" height="10" fill="#333" />
        <g id="arm_visual">
            <line id="robot_line" x1="100" y1="185" x2="100" y2="100" stroke="#00f2ff" stroke-width="10" stroke-linecap="round" />
            <circle id="joint" cx="100" cy="100" r="8" fill="#fff" />
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
    status.innerText = "[ SISTEMA GESTUAL: MANO DETECTADA ]";
    status.style.color = "#00ff00";
    
    const landmarks = results.multiHandLandmarks[0];
    const indexTip = landmarks[8]; // Punta del dedo índice
    
    // Mapear coordenadas de la mano al brazo robótico
    const targetX = 100 + (indexTip.x - 0.5) * 150;
    const targetY = 185 - ((1 - indexTip.y) * 160);
    
    arm.setAttribute('x2', targetX);
    arm.setAttribute('y2', targetY);
    joint.setAttribute('cx', targetX);
    joint.setAttribute('cy', targetY);

    drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {color: '#00f2ff', lineWidth: 3});
    drawLandmarks(canvasCtx, landmarks, {color: '#ffffff', lineWidth: 1, radius: 3});
  } else {
    status.innerText = "[ BUSCANDO MANO... ]";
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
  minDetectionConfidence: 0.6,
  minTrackingConfidence: 0.6
});
hands.onResults(onResults);

const camera = new Camera(video, {
  onFrame: async () => { await hands.send({image: video}); },
  width: 640,
  height: 480
});
camera.start();
</script>
"""

# 3. INTERFAZ GRADIO
with gr.Blocks(theme=gr.themes.Monochrome()) as app:
    gr.Markdown("# 🦾 ADIA v1.2 | Jorge's Engineering Hub")
    
    with gr.Row():
        # LADO IZQUIERDO: CHAT
        with gr.Column(scale=1):
            chatbot = gr.Chatbot(label="ADIA Terminal", height=450)
            msg = gr.Textbox(placeholder="Escribe un comando...", label="Comando")
            with gr.Row():
                btn_canvas = gr.Button("🚀 ACTIVAR CANVAS GESTUAL", variant="primary")
                clear = gr.Button("REINICIAR")

        # LADO DERECHO: CANVAS (Inicia oculto)
        with gr.Column(scale=1, visible=False) as canvas_col:
            gr.Markdown("### 👁️ VISION ENGINE (HAND TRACKING)")
            gr.HTML(vision_pro_html)
            gr.Markdown("#### 📈 TELEMETRÍA EN TIEMPO REAL")
            gr.HTML("<div style='color:lime; font-family:monospace; background:#000; padding:10px; border-radius:5px;'>HAND_POS: ACTIVE | SERVO_A: READY | SYNC: 100%</div>")

    # Lógica de la Interfaz
    def open_canvas():
        return gr.update(visible=True)

    def responder(m, h):
        bot_res = adia_brain(m, h)
        h.append((m, bot_res))
        return "", h

    msg.submit(responder, [msg, chatbot], [msg, chatbot])
    btn_canvas.click(open_canvas, None, canvas_col)
    clear.click(lambda: None, None, chatbot, queue=False)

# 4. LANZAMIENTO (Parche para Render)
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=10000)
