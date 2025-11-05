from flask import Flask, request, render_template_string, jsonify
import threading
import time
import os
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO
import base64

app = Flask(__name__)
client = InferenceClient(token=os.getenv("HF_TOKEN"))

# VARIABLES GLOBALES
video_listo = None
progreso = 0
mensaje = "Listo para generar"

HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AREPA-VIDEO IA</title>
  <style>
    body{font-family:Arial;background:#000;color:#0f0;text-align:center;padding:20px}
    h1{background:linear-gradient(90deg,#f90,#0f0);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .bar{width:90%;height:30px;background:#333;margin:20px auto;border-radius:15px;overflow:hidden}
    .fill{height:100%;width:{{progreso}}%;background:linear-gradient(90deg,#f90,#0f0);transition:1s}
    button,input{padding:15px;font-size:18px;margin:10px;width:90%;border-radius:15px;border:none}
    button{background:#0f0;color:#000;font-weight:bold}
    input{background:#222;color:#fff}
    video{max-width:100%;border-radius:20px;margin:20px 0}
    .download{background:#0f0;color:#000;padding:15px 30px;border-radius:15px;text-decoration:none}
  </style>
</head>
<body>
  <h1>AREPA-VIDEO IA</h1>
  <p>{{mensaje}}</p>
  <div class="bar"><div class="fill"></div></div>
  
  <form id="form">
    <input type="file" name="image" accept="image/*" required>
    <input type="text" name="prompt" placeholder="Ej: haz que baile arepas voladoras" required>
    <button type="submit">¡GENERAR VIDEO!</button>
  </form>
  
  <div id="resultado"></div>

  <script>
    setInterval(() => location.reload(), 8000); // recarga cada 8 seg

    document.getElementById('form').onsubmit = async (e) => {
      e.preventDefault();
      const form = new FormData(e.target);
      await fetch('/', {method:'POST', body:form});
    };
  </script>
</body>
</html>
'''

def generar_en_fondo(imagen, prompt):
    global video_listo, progreso, mensaje
    try:
        progreso = 10
        mensaje = "Subiendo imagen... 10%"
        img = Image.open(imagen).convert("RGB")
        
        progreso = 30
        mensaje = "Enviando a la IA... 30%"
        buf = BytesIO()
        img.save(buf, "PNG")
        
        progreso = 60
        mensaje = "¡La IA está cocinando el video! 60%"
        video_bytes = client.image_to_video(
            image=buf.getvalue(),
            prompt=prompt,
            model="stabilityai/stable-video-diffusion-img2vid-xt",
            num_inference_steps=20
        )
        
        progreso = 100
        mensaje = "¡VIDEO LISTO! Refrescando..."
        b64 = base64.b64encode(video_bytes).decode()
        video_listo = f"data:video/mp4;base64,{b64}"
    except Exception as e:
        mensaje = f"Error: {e}"
        progreso = 0

@app.route('/', methods=['GET', 'POST'])
def home():
    global video_listo, progreso, mensaje
    
    if request.method == 'POST':
        file = request.files['image']
        prompt = request.form['prompt']
        threading.Thread(target=generar_en_fondo, args=(file.stream, prompt)).start()
        progreso = 5
        mensaje = "¡Arepa en marcha! 5%"
    
    video_tag = f'<video controls><source src="{video_listo}" type="video/mp4"></video><br><a href="{video_listo}" download="arepa-video.mp4" class="download">DESCARGAR</a>' if video_listo else ''
    
    return render_template_string(HTML, progreso=progreso, mensaje=mensaje) + video_tag

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
