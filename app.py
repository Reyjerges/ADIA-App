import gradio as gr
import wikipedia

# Configuración inicial
wikipedia.set_lang("es")
IA_NAME = "ADIA"
OPERADOR = "Jorge"

# --- EL CEREBRO DE ADIA ---
# Esta es la base de datos que tú vas a ir llenando
memoria_aprendida = {
    "hola": f"Sistemas activos. Hola, Operador {OPERADOR}.",
    "quien eres": f"Soy {IA_NAME}, tu asistente personal creado en una Lenovo.",
    "cual es tu mision": "Mi misión es aprender de ti y ayudarte con información de Wikipedia."
}

def cerebro_adia(mensaje, historial):
    mensaje_low = mensaje.lower().strip()

    # 1. BUSCAR EN MEMORIA PROPIA (Entrenamiento)
    if mensaje_low in memoria_aprendida:
        return memoria_aprendida[mensaje_low]

    # 2. FUNCIÓN PARA ENTRENAR (Desde el chat)
    # Formato: Aprende: pregunta = respuesta
    if "aprende:" in mensaje_low:
        try:
            # Separamos la instrucción de la información
            datos = mensaje_low.replace("aprende:", "").split("=")
            pregunta = datos[0].strip()
            respuesta = datos[1].strip()
            
            # Guardamos en el diccionario
            memoria_aprendida[pregunta] = respuesta
            return f"✅ Entendido, {OPERADOR}. He guardado '{pregunta}' en mi núcleo de datos."
        except:
            return "Para enseñarme, usa el formato: Aprende: pregunta = respuesta"

    # 3. BUSCAR EN WIKIPEDIA (Si no sabe lo anterior)
    if "busca" in mensaje_low or "que es" in mensaje_low:
        termino = mensaje_low.replace("busca", "").replace("que es", "").strip()
        try:
            return f"🔍 WIKIPEDIA dice: {wikipedia.summary(termino, sentences=2)}"
        except:
            return f"No encontré información sobre '{termino}' en la red."

    # 4. RESPUESTA SI NO SABE NADA
    return f"No tengo '{mensaje}' en mi base de datos, {OPERADOR}. ¿Quieres enseñarme? Escribe -> Aprende: {mensaje} = [tu respuesta]"

# --- CREACIÓN DE LA INTERFAZ ---
app = gr.ChatInterface(
    fn=cerebro_adia,
    title=f"🧠 {IA_NAME} - NÚCLEO",
    description=f"Entrenando a la IA de {OPERADOR}...",
    
)

# --- LANZAMIENTO (Configurado para Render/Nube) ---
if __name__ == "__main__":
    # Importante: server_name "0.0.0.0" permite que se vea en internet
    app.launch(server_name="0.0.0.0", server_port=7860)
