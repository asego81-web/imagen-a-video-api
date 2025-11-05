from flask import Flask, request, render_template_string
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO
import base64, os

app = Flask(__name__)
client = InferenceClient(token=os.getenv("HF_TOKEN"))

HTML_BASE = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AREPA-VIDEO</title>
  <style>
    body {font-family:Arial;background:#000;color:lime;text-align:center;padding:20px}
    h1 {font-size:30px;color:orange}
    input,button {width:90%;padding:15px;margin:10px;border-radius:15px;font-size:20px}
    input {background:#111;color:white;border:2px solid lime}
    button {background:lime;color:black;font-weight:bold}
    .bar {height:40px;background:#333;border-radius:20px;overflow:hidden;margin:20px}
    .fill {height:100%;width:{{progreso}}%;background:orange;transition:1s}
    video {max-width:100%;border-radius:20px;margin:20px}
    .dl {background:lime;color:black;padding:15px 30px;border-radius:15px;text-decoration:none}
  </style>
</head>
<body>
  <h1>AREPA-VIDEO IA</h1>
  <p style="font-size:22px">{{mensaje}}</p>
  <div class="bar"><div class="fill"></div></div>

  <form method="post" enctype="multipart/form-data">
    <input type="file" name="foto" accept="image/*" required>
    <input type="text" name="prompt" placeholder="Ej: arepas volando en la luna" required>
    <button>¡GENERAR VIDEO!</button>
  </form>

  {% if video %}
    <video controls><source src="data:video/mp4;base64,{{video}}" type="video/mp4"></video><br>
    <a href="data:video/mp4;base64,{{video}}" download="arepa.mp4" class="dl">DESCARGAR</a>
  {% endif %}
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # 1. Recibir datos
        file = request.files["foto"]
        prompt = request.form["prompt"]

        # 2. Progreso 20%
        html = HTML_BASE.replace("{{progreso}}", "20").replace("{{mensaje}}", "Subiendo foto... 20%")
        html = html.replace("{% if video %}...{% endif %}", "")
        yield html

        # 3. Leer imagen
        img = Image.open(file.stream).convert("RGB")
        buf = BytesIO()
        img.save(buf, "PNG")
        img_data = buf.getvalue()

        # 4. Progreso 50%
        html = HTML_BASE.replace("{{progreso}}", "50").replace("{{mensaje}}", "Cocinando video... 50%")
        html = html.replace("{% if video %}...{% endif %}", "")
        yield html

        # 5. Generar video
        video_bytes = client.image_to_video(img_data, prompt)
        video_b64 = base64.b64encode(video_bytes).decode()

        # 6. Progreso 100%
        html = HTML_BASE.replace("{{progreso}}", "100").replace("{{mensaje}}", "¡VIDEO LISTO! 🎉")
        html = html.replace("{{video}}", video_b64)
        yield html

    else:
        return HTML_BASE.replace("{{progreso}}", "0").replace("{{mensaje}}", "¡Sube foto + texto!").replace("{% if video %}...{% endif %}", "")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
