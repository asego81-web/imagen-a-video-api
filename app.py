from flask import Flask, request, render_template_string
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO
import base64
import os
import threading

app = Flask(__name__)
client = InferenceClient(token=os.getenv("HF_TOKEN"))

# Estado
status = {"msg": "Listo", "prog": 0, "video": None}

HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AREPA-VIDEO</title>
  <style>
    body{background:#000;color:#0f0;font-family:Arial;text-align:center;padding:20px}
    h1{font-size:28px;background:linear-gradient(90deg,#f90,#0f0);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .box{background:#111;border:3px dashed #0f0;padding:30px;border-radius:20px;margin:20px auto;width:90%;max-width:500px}
    input,button{width:100%;padding:18px;margin:10px 0;border-radius:15px;font-size:18px}
    input{background:#222;color:#fff;border:none}
    button{background:#0f0;color:#000;border:none;font-weight:bold;cursor:pointer}
    .bar{height:35px;background:#333;border-radius:15px;overflow:hidden;margin:20px 0}
    .fill{height:100%;width:{{prog}}%;background:linear-gradient(90deg,#f90,#0f0);transition:0.8s}
    .msg{font-size:22px;margin:15px 0;color:#ff0}
    video{max-width:100%;border-radius:20px;margin:20px 0}
    .dl{background:#0f0;color:#000;padding:15px 30px;border-radius:15px;text-decoration:none;display:inline-block}
  </style>
</head>
<body>
  <h1>AREPA-VIDEO IA</h1>
  <div class="msg">{{msg}}</div>
  <div class="bar"><div class="fill"></div></div>

  <form method="post" enctype="multipart/form-data">
    <div class="box">
      <input type="file" name="image" accept="image/*" required style="cursor:pointer">
    </div>
    <input type="text" name="prompt" placeholder="Ej: haz que baile arepas voladoras" required>
    <button>¡GENERAR VIDEO!</button>
  </form>

  {% if video %}
    <video controls><source src="{{video}}" type="video/mp4"></video><br>
    <a href="{{video}}" download="arepa.mp4" class="dl">DESCARGAR</a>
  {% endif %}

  <script>
    setInterval(() => location.reload(), 7000);
  </script>
</body>
</html>
'''

def generar(imagen, prompt):
    global status
    try:
        status["msg"] = "Subiendo... 15%"
        status["prog"] = 15
        img = Image.open(imagen).convert("RGB")
        buf = BytesIO()
        img.save(buf, "PNG")

        status["msg"] = "Cocinando video... 50%"
        status["prog"] = 50
        video_bytes = client.image_to_video(
            image=buf.getvalue(),
            prompt=prompt,
            model="stabilityai/stable-video-diffusion-img2vid-xt
