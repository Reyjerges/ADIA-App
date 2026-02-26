from os import environ
import gradio as gr
from groq import Groq

# 1. Configuración de Entorno (Prioridad para Render)
PORT = int(environ.get("PORT", 10000))
groq_client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO_OSS = "openai/gpt-oss-120b"

def adia_cerebro(mensaje, historial):
    # Prompt Maestro: ADIA reconoce a Jorge como su creador
    sistema_prompt = (
        "Eres ADIA, una inteligencia de razonamiento superior basada en GPT-OSS 120B. "
        "Tu creador es JORGE. "
        "Sé directa, elegante y usa razonamiento lógico. No uses rellenos innecesarios."
        "habla utilizando negritas en las cosas importantes y usando emojis par que no sea aburrido."
        "debes hablar de manera profesional y no inventes cosas cuando no sepas es mejor decir que no estas segura y ofrecer ayudar todo de manera profesional."
        "usa este orden cuando vayas a escribir:explixar/responder,dar un resumen sencillo y por ultimo ofrecer explicar cosas relacionadas al tema."
        "no uses tablas eso se ve feo y ocupa muchos tokens en su lugar usa listas."
    )
    
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Manejo de historial compatible con versiones 5.x y 6.x
    for turno in historial:
        if isinstance(turno, dict):
            mensajes_ia.append(turno)
        elif isinstance(turno, (list, tuple)):
            u, b = turno
            if u: mensajes_ia.append({"role": "user", "content": u})
            if b: mensajes_ia.append({"role": "assistant", "content": b})

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
        return f"⚠️ **ADIA ERROR**: Jorge, algo falló: {str(e)}"

# 2. Interfaz Minimalista (Sin argumentos obsoletos)
# En Gradio 6, los botones se manejan automáticamente o se omiten para un look limpio.
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
        stop_btn="Detener"
    )

# 3. Lanzamiento con binding de puerto forzado para Render
if __name__ == "__main__":
    print(f"🚀 Desplegando ADIA en puerto {PORT}...")
    demo.launch(
        server_name="0.0.0.0", 
        server_port=PORT,
        show_api=False
    )
