import os
import gradio as gr
from groq import Groq

# 1. Configuración del Cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def buscar_en_google(consulta):
    # Importamos dentro de la función para que no rompa el inicio del servidor
    try:
        from googlesearch import search
        resultados = []
        # Buscamos solo 3 links rápidos
        for url in search(consulta, num_results=3, lang="es"):
            resultados.append(url)
        
        if resultados:
            links = "\n".join(resultados)
            return f"\n\n[Fuentes encontradas]:\n{links}"
        else:
            return ""
    except Exception:
        return ""

def chat_adia(mensaje, historial):
    instrucciones = (
        "Eres ADIA, la IA de Jorge. Nombre: Advanced Digital Intelligence Assistant. "
        "Eres su compañera técnica y creativa. Responde de forma clara y directa."
    )
    
    # Detectamos si quiere buscar algo
    info_extra = ""
    palabras_busqueda = ["busca", "quien es", "que es", "noticias", "precio"]
    if any(palabra in mensaje.lower() for palabra in palabras_busqueda):
        info_extra = buscar_en_google(mensaje)

    mensajes_para_groq = [{"role": "system", "content": instrucciones}]
    
    # Limpieza de historial para Gradio 5
    for h in historial:
        if isinstance(h, dict):
            rol = h.get("role", "user")
            contenido = h.get("content", "")
            if isinstance(contenido, list):
                contenido = contenido[0].get("text", "")
            mensajes_para_groq.append({"role": rol, "content": str(contenido)})
        elif isinstance(h, (list, tuple)):
            mensajes_para_groq.append({"role": "user", "content": str(h[0])})
            mensajes_para_groq.append({"role": "assistant", "content": str(h[1])})

    mensajes_para_groq.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_para_groq,
            temperature=0.7
        )
        respuesta_final = completion.choices[0].message.content
        return respuesta_final + info_extra
    except Exception as e:
        return f"Error en el cerebro de ADIA: {str(e)}"

# Interfaz
demo = gr.ChatInterface(fn=chat_adia, title="ADIA")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
