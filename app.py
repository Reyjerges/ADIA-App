from os import environ
import gradio as gr
from groq import Groq

# 1. Configuración de Puerto para Render (Prioridad Alta)
PORT = int(environ.get("PORT", 10000))
groq_client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO_OSS = "openai/gpt-oss-120b"

def adia_cerebro(mensaje, historial):
    # Prompt Maestro para ADIA
    sistema_prompt = (
        "Eres ADIA, IA de élite basada en GPT-OSS 120B. Tu creador es JORGE. "
        "Trátalo con lealtad y prioridad absoluta. Sé directa, brillante y lógica. "
        "No uses introducciones vacías, ve al grano con excelencia."
    )
    
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Manejo de historial manual (sin depender de 'type')
    for turno in historial:
        # Gradio clásico envía [usuario, bot]
        if isinstance(turno, (list, tuple)):
            u, b = turno
            if u: mensajes_ia.append({"role": "user", "content": u})
            if b: mensajes_ia.append({"role": "assistant", "content": b})
        # Gradio nuevo envía {'role': '...', 'content': '...'}
        elif isinstance(turno, dict):
            mensajes_ia.append(turno)

    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        completion = groq_client.chat.completions.create(
            model=MODELO_OSS,
            messages=mensajes_ia,
            temperature=0.6,
            max_tokens=2500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ **ADIA CORE ERROR**: Jorge, algo falló: {str(e)}"

# 2. Interfaz Limpia (Sin argumentos problemáticos)
custom_css = "footer { display: none !important; } .gradio-container { max-width: 850px !important; }"

with gr.Blocks(title="ADIA Core") as demo:
    gr.Markdown("<h2 style='text-align: center;'>ADIA Intelligence</h2>")
    gr.Markdown("<p style='text-align: center;'>Sistema Operado por Jorge</p>")
    
    gr.ChatInterface(
        fn=adia_cerebro,
        chatbot=gr.Chatbot(
            show_label=False, 
            height=600,
            avatar_images=(None, "https://api.dicebear.com")
        ),
        submit_btn="Enviar",
        retry_btn="🔄 Reintentar",
        clear_btn="🗑️ Borrar"
    )

# 3. Lanzamiento Crítico para Render
if __name__ == "__main__":
    print(f"🚀 Iniciando ADIA en el puerto {PORT}...")
    demo.launch(
        server_name="0.0.0.0", 
        server_port=PORT,
        css=custom_css,
        share=False,
        show_api=False
    )
