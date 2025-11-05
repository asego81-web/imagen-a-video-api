from flask import Flask, request, render_template_string
import threading, time, os, base64
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO

app = Flask(__name__)
client = InferenceClient(token=os.getenv("HF_TOKEN"))

# Estado
p = 5
msg = "¡Sube foto y texto!"
video = ""

HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AREPA-VIDEO</title>
<style>
  body{background:#000;color:lime;font:20px Arial;text-align:center;padding:20px}
  input,button{width:90%;padding:15px;margin:10px;border-radius:15px;font-size:20px}
  input{background:#111;color:white;border:2px solid lime}
  button{background:lime;color:black}
  .bar{height:40px;background:#333;border-radius:20px;overflow:hidden;margin:20px}
  .fill{height:100%;width:%d%%;background:orange}
  video{max-width:100%;border-radius:20px}
</style></head><body>
<h1 style="color:orange">AREPA-VIDEO</h1>
<p>%s</p>
<div class="bar"><div class="fill"></div></div>

<form method=post enctype=multipart/form-data>
  <input type=file name=f required>
  <input type=text name=t placeholder="Ej: arepas volando" required>
  <button>¡VIDEO!</button>
</form>

%s
<script>
  setTimeout(() => location.reload(), 12000); // 12 seg seguros
</script>
</body></html>
""" % (p, msg, '<video controls><source src="'+video+'" type="video/mp4"></video><br><a href="'+video+'" download="arepa.mp4" style="background:lime;color:black;padding:15px 30px;border-radius:15px;text-decoration:none">DESCARGAR</a>' if video else "")

def crear():
    global p, msg, video, HTML
    p = 20; msg = "Foto recibida..."; actualizar()
    time.sleep(2)
    p = 50; msg = "IA cocinando arepas..."; actualizar()
    time.sleep(2)
    
    img = Image.open(request.files["f"].stream)
    buf = BytesIO(); img.save(buf, "PNG")
    
    vid = client.image_to_video(buf.getvalue(), request.form["t"])
    video = "data:video/mp4;base64," + base64.b64encode(vid).decode()
    p = 100; msg = "¡VIDEO LISTO! 🎉"
    actualizar()

def actualizar():
    global HTML
    HTML = """
    <!DOCTYPE html>
    <html><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AREPA-VIDEO</title>
    <style>
      body{background:#000;color:lime;font:20px Arial;text-align:center;padding:20px}
      input,button{width:90%;padding:15px;margin:10px;border-radius:15px;font-size:20px}
      input{background:#111;color:white;border:2px solid lime}
      button{background:lime;color:black}
      .bar{height:40px;background:#333;border-radius:20px;overflow:hidden;margin:20px}
      .fill{height:100%;width:%d%%;background:orange}
      video{max-width:100%;border-radius:20px}
    </style></head><body>
    <h1 style="color:orange">AREPA-VIDEO</h1>
    <p>%s</p>
    <div class="bar"><div class="fill"></div></div>
    %s
    <script>
      setTimeout(() => location.reload(), 12000);
    </script>
    </body></html>
    """ % (p, msg, '<video controls><source src="'+video+'" type="video/mp4"></video><br><a href="'+video+'" download="arepa.mp4" style="background:lime;color:black;padding:15px 30px;border-radius:15px;text-decoration:none">DESCARGAR</a>' if video else "<form method=post enctype=multipart/form-data><input type=file name=f required><input type=text name=t placeholder='Ej: arepas volando' required><button>¡VIDEO!</button></form>")

@app.route("/", methods=["GET","POST"])
def home():
    global HTML
    if request.method == "POST":
        threading.Thread(target=crear).start()
        p = 10; msg = "¡Em
