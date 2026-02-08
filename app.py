import os
import gradio as gr
from groq import Groq
import plotly.graph_objects as go
import numpy as np

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Esta función crea la figura 3D
def generar_figura_3d(tipo):
    if "esfera" in tipo.lower():
        # Matemáticas para una esfera
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = np.cos(u)*np.sin(v)
        y = np.sin(u)*np.sin(v)
        z = np.cos(v)
        fig = go.Figure(data=[go.Surface(x=x, y=y, z=z, colorscale='Viridis')])
    else:
        # Una forma abstracta por defecto (tipo Jarvis)
        z = np.random.standard_normal((10, 10))
        fig = go.Figure(data=[go.Surface(z=z, colorscale='Electric')])
    
    fig.update_layout(title='ADIA Visual System', autosize=True,
                  margin=dict(l=0, r=0, b=0, t=0), template="plotly_dark")
    return fig

def chat_adia(mensaje, historial):
    # Instrucciones para que ADIA sepa que puede mostrar 3D
    instrucciones = "Eres ADIA. Si Jorge pide ver algo en 3D, dile que lo estás proyectando."
    
    # (Aquí iría tu lógica de historial que ya tenemos)
    
    # Por ahora, vamos a devolver un texto y la figura
    return "Proyectando interfaz 3D...", generar_figura_3d(mensaje)

# Interfaz con espacio para el Chat y el Holograma
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# ADIA - Interface JARVIS")
    with gr.Row():
        with gr.Column(scale=1):
            chatbot = gr.Chatbot(label="ADIA Chat")
            msg = gr.Textbox(label="Orden")
        with gr.Column(scale=1):
            plot = gr.Plot(label="Proyección Holográfica")

    def responder(mensaje, chat_history):
        bot_msg, fig = chat_adia(mensaje, chat_history)
        chat_history.append((mensaje, bot_msg))
        return chat_history, fig

    msg.submit(responder, [msg, chatbot], [chatbot, plot])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
  
