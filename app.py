import os
import datetime
import gradio gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de herramientas
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    # Hora para que la IA sepa qué día es hoy
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Instrucción de identidad: Normal y directa
    system_prompt = (
        f"Eres ADIA. Jorge es tu único creador. "
        f"Habla de forma normal, clara y educada. "
        "No uses tonos robóticos ni pretenciosos. "
        "Usa los datos de red que te pase el sistema para dar información real de hoy."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Manejo de historial compatible con Render
    for chat in history:
        if isinstance(chat, dict):
            messages.append({"role": chat["role"], "content": chat["content"]})
        else:
            messages.append({"role": "user", "content": chat})
            messages.append({"role": "assistant", "content": chat})

    # 2. BÚSQUEDA TAVILY CORREGIDA (Para el precio real)
    search_context = ""
    # Palabras que activan la búsqueda
    if any(p in message.lower() for p in ["precio", "bitcoin", "valor", "noticias", "clima"]):
        try:
            # Buscamos la información más fresca
            search = tavily.search(query=f"{message} hoy {ahora}", search_depth="basic", max_results=1)
            if search and "results" in search and len(search["results"]) > 0:
                # Extraemos el texto real del primer resultado
                info_fresca = search["results"][0].get("content", "")
                search_context = f"\n\n[DATOS DE INTERNET ACTUALIZADOS]: {info_fresca}"
        except:
            search_context = "\n\n[SISTEMA: Error al conectar con los servidores de datos]"

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        # 3. Generación con el modelo 120B
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=messages,
            temperature=0.6, # Temperatura media para que sea natural
            stream=True 
        )
        
        texto_acumulado = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                texto_acumulado += chunk.choices[0].delta.content
                yield texto_acumulado
                
    except Exception as e:
        yield f"Hubo un error en el sistema, Jorge: {str(e)}"

# Interfaz limpia
demo = gr.ChatInterface(fn=adia_chat, title="ADIA")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)

