from flask import Flask, request, render_template_string
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO
import base64, os, time

app = Flask(__name__)
client = InferenceClient(token=os.getenv("HF_TOKEN"))

# Estado
p = 0
msg = "¡Sube foto + texto!"
video = ""

HTML = '''
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AREPA-VIDEO</title>
<style>
  body{background:#000;color:lime;font:20px Arial;text-align:center;padding:20px}
  h1{color:orange}
  input,button{width:90%;padding:15px;margin:10px;border-radius:15px;font-size:20px}
  input{background:#111;color:white;border:2px solid lime}
  button{background:lime;color:black}
  .bar{height:40px;background:#333;border-radius:20px;overflow:hidden;margin:20px}
  .fill{height:100%;width:{{p}}%;background:orange;transition:1s}
  video{max-width:100%;border-radius:20px;margin:20px}
  .dl{background:lime;color:black;padding:15px 30px;border-radius:15px;text-decoration:none}
</style></head><body>
<h1>AREPA-VIDEO</h1>
<p>{{msg}}</p>
<div class="bar"><div class="fill"></div></div>

<form method=post enctype=multipart/form-data>
  <input type=file name=f required accept="image/*">
  <input type=text name=t placeholder="Ej: arepas volando" required>
  <button>¡VIDEO!</button>
</form>

{% if video %}
<video controls><source src="data:video/mp4;base64,{{video}}" type="video/mp4"></video><br>
<a href="data:video/mp4;base64,{{video}}" download="arepa.mp4" class="dl">DESCARGAR</a>
{% endif %}

<script>
  // Recarga cada 12 seg (seguro)
  setTimeout(() => location.reload(), 12000);
</script>
</body></html>
'''

@app.route("/", methods=["GET","POST"])
def home():
    global p, msg, video
    if request.method == "POST":
        p = 10
        msg = "¡Arepa en marcha! 10%"
        file = request.files["f"]
        prompt = request.form["t"]

        # 20%
        p = 20
        msg = "Leyendo foto... 20%"
        img = Image.open(file.stream).convert("RGB")
        buf = BytesIO()
        img.save(buf, "PNG")
        img_data = buf.getvalue()

        # 50%
        p = 50
        msg = "Cocinando video... 50%"
        video_bytes = client.image_to_video(img_data, prompt)

        # 100%
        video = base64.b64encode(video_bytes).decode()
        p = 100
        msg = "¡VIDEO LISTO! 🎉"

    return render_template_string(HTML, p=p, msg=msg, video=video)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
