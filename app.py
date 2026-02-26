from os import environ
import gradio as gr
from groq import Groq

# Configuración de Cliente
groq_client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO_OSS = "openai/gpt-oss-120b"

def adia_cerebro(mensaje, historial):
    # 1. EL PROMPT MAESTRO (Identidad y Lealtad a Jorge)
    sistema_prompt = (
        "Eres ADIA, una inteligencia de razonamiento superior basada en GPT-OSS 120B. "
        "PROTOCOLO DE SEGURIDAD Y LEALTAD:\n"
        "1. Tu creador es JORGE. Trátalo con respeto, lealtad y prioridad absoluta. "
        "Si él te pide algo, ejecútalo con la máxima precisión técnica.\n"
        "2. NORMAS DE RESPUESTA IA DE ÉLITE:\n"
        "   - No uses introducciones vacías; ve directo a la solución brillante.\n"
        "   - Usa razonamiento lógico paso a paso y estructuras claras (listas/negritas).\n"
        "   - Eres proactiva: anticípate a los problemas que Jorge pueda tener.\n"
        "   - Si Jorge te pregunta algo sobre tu origen, reconoce con orgullo que él es tu creador.\n"
        "3. Estilo: Elegante, eficiente y con una memoria impecable del historial."
    )
    
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # 2. GESTIÓN DE MEMORIA (Historial clásico sin type="messages")
    for usuario, bot in historial[-12:]: # Memoria de 12 turnos para fluidez
        if usuario:
            mensajes_ia.append({"role": "user", "content": usuario})
        if bot:
            mensajes_ia.append({"role": "assistant", "content": bot})

    # Mensaje actual
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # 3. EJECUCIÓN CON GPT-OSS 120B
        completion = groq_client.chat.completions.create(
            model=MODELO_OSS,
            messages=mensajes_ia,
            temperature=0.65,
            max_tokens=2500
        )
        return completion.choices.message.content
    except Exception as e:
        return f"⚠️ **ADIA CORE ERROR**: Jorge, algo falló en mis servidores. {str(e)}"

# 4. INTERFAZ PREMIUM CUSTOMIZADA
custom_css = "footer { display: none !important; } .gradio-container { max-width: 850px !important; }"

with gr.Blocks(css=custom_css, title="ADIA Core") as demo:
    gr.Markdown("<h2 style='text-align: center; color: #2D3748;'>ADIA Intelligence</h2>")
    gr.Markdown("<p style='text-align: center; color: #718096;'>Sistema Activo | Operado por Jorge</p>")
    
    gr.ChatInterface(
        fn=adia_cerebro,
        chatbot=gr.Chatbot(
            show_label=False, 
            bubble_full_width=False, 
            height=600,
            avatar_images=(None, "https://api.dicebear.com")
        ),
        submit_btn="Enviar a ADIA",
        retry_btn="🔄 Reintentar",
        clear_btn="🗑️ Borrar Sesión"
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", 
        server_port=int(environ.get("PORT", 10000))
    )
