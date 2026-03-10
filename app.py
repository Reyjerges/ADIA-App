import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# 1. Configuración de Clientes
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_chat(message, history):
    # PERSONALIDAD SOFISTICADA (Problema 3)
    system_prompt = (
        "Eres ADIA, una inteligencia artificial de élite creada por Jorge. "
        "Jorge es tu creador; trátalo con el máximo respeto y lealtad. "
        "Tu lenguaje es sofisticado, profesional y de alta tecnología. "
        "REGLA DE ORO: Sé eficiente. No uses rellenos. Si la respuesta es corta, mantenla corta pero elegante."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # MEMORIA DE SESIÓN (Problema 1)
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})
    
    # BÚSQUEDA TAVILY CORREGIDA (Problema 2)
    search_context = ""
    trigger = ["quién es", "qué es", "noticias", "precio", "cuándo"]
    
    if any(p in message.lower() for p in trigger) and len(message) > 4:
        try:
            search = tavily.search(query=message, search_depth="basic", max_results=1)
            # Acceso seguro a los resultados de Tavily
            if search and "results" in search and len(search["results"]) > 0:
                res = search["results"][0].get("content", "")
                search_context = f"\n\n[Información de red: {res}]"
        except:
            search_context = ""

    messages.append({"role": "user", "content": f"{message}{search_context}"})

    try:
        # MODELO OPENAI OSS 120B
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=messages,
            temperature=0.5,
            stream=True 
        )
        
        response_text = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
                yield response_text # Efecto palabra por palabra
                
    except Exception as e:
        yield f"Señor Jorge, detecto una anomalía en el núcleo 120B: {str(e)}"

# INTERFAZ ULTRA COMPATIBLE (Sin el error de 'type')
demo = gr.ChatInterface(
    fn=adia_chat,
    title="ADIA | Advanced Intelligence",
    description="Protocolo de soporte para el Señor Jorge operativo."
)

if __name__ == "__main__":
    # Render asigna el puerto automáticamente
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
