from flask import Flask, request, render_template_string
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO
import base64, os, threading, time

app = Flask(__name__)
client = InferenceClient(token=os.getenv("HF_TOKEN"))

# Variables globales
progreso = 0
mensaje = "¡Sube foto + texto!"
video_b64 = None

HTML = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AREPA-VIDEO</title>
  <style>
    body {font-family:Arial;background:#000;color:lime;text-align:center;padding:20px}
    input,button {width:90%;padding:15px;margin:10px;font-size:20px;border-radius:15px}
    input {background:#111;color:white;border:2px solid lime}
    button {background:lime;color:black;font-weight:bold}
    .bar {height:40px;background:#333;border-radius:20px;overflow:hidden;margin:20px}
    .fill {height:100%;width:{{progreso}}%;background:orange;transition:1s}
    video {max-width:100%;border-radius:20px;margin:20px}
    .dl {background:lime;color:black;padding:15px 30px;border-radius:15px;text-decoration:none}
  </style>
</head>
<body>
  <h1 style="color:orange">AREPA-VIDEO IA</h1>
  <p style="font-size:22px">{{mensaje}}</p>
  <div class="bar"><div class="fill"></div></div>

  <form method="post" enctype="multipart/form-data">
    <input type="file" name="foto" accept="image/*" required>
    <input type="text" name="texto" placeholder="Ej: arepas volando en la luna" required>
    <button>¡CREAR VIDEO!</button>
  </form>

  {% if video %}
    <video controls><source src="data:video/mp4;base64,{{video}}" type="video/mp4"></video><br>
    <a href="data:video/mp4;base64,{{video}}" download="arepa.mp4" class="dl">DESCARGAR</a>
  {% endif %}

  <script>
    setTimeout(() => location.reload(), 12000);
  </script>
</body>
</html>
'''

def generar_video():
    global progreso, mensaje, video_b64
    try:
        # 1. Recibir archivo
        file = request.files['foto']
        prompt = request.form['texto']
        progreso = 20
        mensaje = "Foto recibida... 20%"

        # 2. Leer imagen
        img_bytes = file.read()
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        buf = BytesIO()
        img.save(buf, "PNG")
        img_png = buf.getvalue()

        progreso = 50
        mensaje = "IA cocinando arepas... 50%"

        # 3. Generar video
        video_bytes = client.image_to_video(img_png, prompt)
        video_b64 = base64.b64encode(video_bytes).decode()

        progreso = 100
        mensaje = "¡VIDEO LISTO! 🎉"
    except Exception as e:
        mensaje = f"Error: {e}"
        progreso = 0

@app.route("/", methods=["GET", "POST"])
def home():
    global progreso, mensaje, video_b64

    if request.method == "POST":
        threading.Thread(target=generar_video).start()
        progreso = 10
        mensaje = "¡Empezando! 10%"

    return render_template_string(HTML, progreso=progreso, mensaje=mensaje, video=video_b64)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
