import os
import gradio as gr
from groq import Groq

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY no está configurada")

client = Groq(api_key=api_key)

def chat_adia(mensaje, audio_input, historial):
    if historial is None:
        historial = []
    
    if audio_input is not None:
        try:
            with open(audio_input, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                )
                mensaje = transcript.text
        except Exception as e:
            return f"Error al procesar audio: {str(e)}", None
    
    instrucciones = (
        "Eres ADIA (Advanced Digital Intelligence Architecture). Tu nombre significa 'Vida'. "
        "Eres la IA personal de Jorge. Tienes MEMORIA TOTAL. "
        "Si Jorge pregunta por algo dicho anteriormente, revisa el historial. "
        "\n\nMODULO DE IMAGEN: Si pide un dibujo, responde EXCLUSIVAMENTE con: "
        "![imagen](https://pollinations.ai/p/PROMPT?width=1080&height=1080&nologo=true) "
        "Traduce PROMPT al inglés y usa guiones medios."
    )
    
    mensajes = [{"role": "system", "content": instrucciones}]
    
    for h in historial:
        if isinstance(h, dict):
            mensajes.append(h)
        else:
            mensajes.append({"role": "user", "content": h[0]})
            mensajes.append({"role": "assistant", "content": h[1]})
            
    mensajes.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.7
        )
        respuesta = completion.choices[0].message.content
        return respuesta, respuesta
    except Exception as e:
        return f"Error: {str(e)}", None

with gr.Blocks() as demo:
    gr.Markdown("# ADIA v2.1 - Con Voz")
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(label="Grabar mensaje", type="filepath")
            text_input = gr.Textbox(label="O escribe aqui", placeholder="Escribe tu mensaje...")
            submit_btn = gr.Button("Enviar", variant="primary")
        
        with gr.Column():
            text_output = gr.Textbox(label="Respuesta", interactive=False)
            audio_output = gr.Audio(label="Respuesta en voz")
    
    chat_history = gr.State(value=[])
    
    def process_input(audio, text, history):
        user_input = text if text else ""
        response, audio_resp = chat_adia(user_input, audio, history)
        
        if history is None:
            history = []
        history.append({"role": "user", "content": user_input or "[Audio]"})
        history.append({"role": "assistant", "content": response})
        
        return response, audio_resp, history
    
    submit_btn.click(
        process_input,
        inputs=[audio_input, text_input, chat_history],
        outputs=[text_output, audio_output, chat_history]
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=port)
