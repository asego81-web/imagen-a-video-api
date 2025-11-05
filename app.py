from flask import Flask, request, render_template_string
import threading, time, os, base64
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO

app = Flask(__name__)
client = InferenceClient(token=os.getenv("HF_TOKEN"))

estado = {"texto": "¡Sube una foto!", "porc": 0, "video": ""}

HTML = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body{font-family:Arial;background:#000;color:lime;text-align:center;padding:20px}
  h1{font-size:30px;color:orange}
  input,button{width:90%;padding:15px;margin:10px;font-size:20px;border-radius:15px}
  input{background:#222;color:white;border:none}
  button{background:lime;color:black;font-weight:bold}
  .barra{height:30px;background:#333;border-radius:15px;overflow:hidden;margin:20px}
  .fill{height:100%;width:{{porc}}%;background:orange;transition:1s}
  video{max-width:100%;border-radius:20px;margin:20px}
  .dl{background:lime;color:black;padding:15px 30px;border-radius:15px;text-decoration:none}
</style></head><body>
<h1>AREPA-VIDEO</h1>
<p style="font-size:22px">{{texto}}</p>
<div class="barra"><div class="fill"></div></div>

<form method=post enctype=multipart/form-data>
  <input type=file name=foto accept="image/*" required>
  <input type=text name=idea placeholder="Ej: bailando arepas voladoras" required>
  <button>¡CREAR VIDEO!</button>
</form>

{% if video %}
<video controls><source src="{{video}}" type="video/mp4"></video><br>
<a href="{{video}}" download="arepa.mp4" class="dl">DESCARGAR</a>
{% endif %}

<!-- SOLO REFRESCA CUANDO TRABAJA -->
<script>
  setTimeout(() => location.reload(), 15000);  // 15 segundos seguros
</script>
</body></html>
"""

def hacer_video(foto, idea):
    global estado
    estado["texto"] = "Subiendo foto... 20%"
    estado["porc"] = 20
    time.sleep(1)
    
    img = Image.open(foto).convert("RGB")
    buf = BytesIO()
    img.save(buf, "PNG")
    
    estado["texto"] = "La IA está cocinando... 60%"
    estado["porc"] = 60
    time.sleep(1)
    
    video = client.image_to_video(buf.getvalue(), idea)
    b64 = base64.b64encode(video).decode()
    estado["video"] = f"data:video/mp4;base64,{b64}"
    estado["texto"] = "¡VIDEO LISTO! 🎉"
    estado["porc"] = 100

@app.route("/", methods=["GET","POST"])
def inicio():
    if request.method == "POST":
        threading.Thread(target=hacer_video, 
                        args=(request.files["foto"].stream, request.form["idea"])).start()
        estado["texto"] = "¡Arepa en marcha! 5%"
        estado["porc"] = 5
    
    return render_template_string(HTML, **estado)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
