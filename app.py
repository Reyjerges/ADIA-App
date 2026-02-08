import os
import gradio as gr
from groq import Groq
from googlesearch import search

# 1. Configuración del Cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def buscar_en_google(consulta):
    """Función para que ADIA busque links en internet"""
    try:
        resultados = []
        # Busca los 3 mejores resultados
        for url in search(consulta, num_results=3, lang="es"):
            resultados.append(url)
        
        if resultados:
            links = "\n".join(resultados)
            return f"\n\nJorge, he encontrado estos enlaces que te pueden servir:\n{links}"
        else:
            return "\n\nNo encontré enlaces recientes sobre eso."
    except Exception:
        return "\n\n(Nota: Tuve un problema al conectar con Google, pero aquí tienes mi respuesta basada en mi memoria...)"

def chat_adia(mensaje, historial):
    # Instrucciones de identidad (Ancla)
    instrucciones = (
        "Eres ADIA, la IA de Jorge. Nombre: Advanced Digital Intelligence Assistant. "
        "Eres su compañera técnica y creativa. Habla de forma natural. "
        "Si Jorge te pide que 'busques' algo, indícale que estás consultando fuentes externas."
    )
    
    # Si el usuario pide buscar, activamos la función de búsqueda
    respuesta_extra = ""
    if "busca" in mensaje.lower() or "quien es" in mensaje.lower() or "que es" in mensaje.lower():
        respuesta_extra = buscar_en_google(mensaje)

    mensajes_para_groq = [{"role": "system", "content": instrucciones}]
    
    # 2. LIMPIEZA DEL HISTORIAL
    for h in historial:
        if isinstance(h, dict):
            rol = h.get("role", "user")
            contenido = h.get("content", "")
            if isinstance(contenido, list) and len(contenido) > 0:
                contenido = contenido[0].get("text", "")
            if rol and contenido:
                mensajes_para_groq.append({"role": rol, "content": str(contenido)})
