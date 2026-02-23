import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Configuración de Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    contexto_web = ""
    
    # Solo buscamos en la web si el mensaje es una pregunta real (más de 3 palabras)
    palabras = mensaje.split()
    if len(palabras) > 3:
        try:
            search_result = tavily.search(query=mensaje, search_depth="basic", max_results=1)
            if search_result['results']:
                contexto_web = search_result['results'][0]['content']
        except Exception:
            contexto_web = ""

    # Instrucciones de personalidad para Gemma (más natural)
    mensajes_ia = [{
        "role": "system", 
        "content": (
            "Eres ADIA. Una asistente avanzada, lógica y equilibrada. "
            "Tu trato con Jorge es cercano pero profesional. "
            "Responde de forma natural sin soltar discursos de seguridad innecesarios. "
            f"Contexto actual: {contexto_web}"
        )
    }]
    
    # Memoria de conversación
    ventana_memoria = historial[-5:] if len(historial) > 5 else historial
    for h_user, h_bot in ventana_memoria:
        if h_user: mensajes_ia.append({"role": "user", "content": h_user})
        if h_bot: mensajes_ia.append({"role": "assistant", "content": h_bot})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # Probamos con Gemma 2 9B: Excelente razonamiento y muy estable
        respuesta = groq_client.chat.completions.create(
            model="gemma2-9b-it", 
            messages=mensajes_ia,
            temperature=0.6,
            max_tokens=1000
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"ADIA en pausa: {str(e)}"

# Interfaz
demo = gr.ChatInterface(
    fn=adia_cerebro, 
    title="ADIA v2.8",
    description="Motor: Gemma 2 9B | Modo Estabilizado"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
