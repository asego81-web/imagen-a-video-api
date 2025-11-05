from flask import Flask, request, render_template_string
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO
import base64
import os
import threading

app = Flask(__name__)
client = InferenceClient(token=os.getenv("HF_TOKEN"))

# Estado global
status = {"msg": "¡Sube una foto y escribe tu idea!", "prog": 0, "video": None, "working": False}

HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AREPA-VIDEO IA</title>
  <style>
    body{background:#000;color:#0f0;font-family:Arial;text-align:center;padding:20px}
    h1{font-size:28px;background:linear-gradient(90deg,#f90,#0f0);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .box{background:#111;border:3px dashed #0f0;padding:40px;border-radius:20px;margin:20px auto;width:90%;max-width:500px;position:relative}
    .file-input{width:100%;height:100%;position:absolute;opacity:0;cursor:pointer}
    input[type="text"],button{width:90%;padding:18px;margin:10px auto;border-radius:15px;font-size:18px}
    input[type="text"]{background:#222;color:#fff;border:none}
    button{background:#0f0;color:#000;border:none;font-weight:bold;cursor:pointer}
    .bar{height:35px;background:#333;border-radius:15px;overflow:hidden;margin:20px auto;width:90%}
    .fill{height:100%;width:{{prog}}%;background:linear-gradient(90deg,#f90,#0f0);transition:0.8s}
    .msg{font-size:20px;margin:15px 0;color:#ff0}
    video{max-width:100%;border-radius:20px;margin:20px 0}
    .dl{background:#0f0;color:#000;padding:15px 30px;border-radius:15px;text-decoration:none;display:inline-block}
  </style>
</head>
<body>
  <h1>AREPA-VIDEO IA</h1>
  <div class="msg">{{msg}}</div>
  <div class="bar"><div class="fill"></div></div>

  <form method="post" enctype="multipart/form-data" id="form">
    <div class="box">
      <div>📸 TOCA AQUÍ PARA SUBIR FOTO</div>
      <input type="file" name="image" accept="image/*" required class="file-input">
    </div>
    <input type="text" name="prompt" placeholder="Ej: haz que baile arepas voladoras" required>
    <button>¡GENERAR VIDEO!</button>
  </form>

  {% if video %}
    <video controls><source src="{{video}}" type="video/mp4"></video><br>
    <a href="{{video}}" download="arepa.mp4" class="dl">DESCARGAR</a>
  {% endif %}

  <script>
    // Solo recarga si está trabajando
    setInterval(() => {
      if ({{ "true" if working else "false" }}) location.reload();
    }, 10000);
  </script>
</body>
</html>
'''

def generar(imagen, prompt):
    global status
    status["working"] = True
    try:
        status["msg"] = "Subiendo foto... 20%"
        status["prog"] = 20
        img = Image.open(imagen).convert("RGB")
        buf = BytesIO()
        img.save(buf, "PNG")

        status["msg"] = "La IA está cocinando... 60%"
        status["prog"] = 60
        video_bytes = client.image_to_video(
            image=buf.getvalue(),
            prompt=prompt,
            model="stabilityai/stable-video-diffusion-img2vid-xt",
            num_inference_steps=20
        )

        b64 = base64.b64encode(video_bytes).decode()
        status["video"] = f"data:video/mp4;base64,{b64}"
        status["msg"] = "¡VIDEO LISTO! 🎉"
        status["prog"] = 100
    except Exception as e:
        status["msg"] = f"Error: {e}"
        status["prog"] = 0
    status["working"] = False

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST' and not status["working"]:
        threading.Thread(target=generar, args=(request.files['image'].stream, request.form['prompt'])).start()
        status["msg"] = "¡Arepa en marcha! 5%"
        status["prog"] = 5

    return render_template_string(HTML,
        msg=status["msg"],
        prog=status["prog"],
        video=status["video"],
        working="true" if status["working"] else "false"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
