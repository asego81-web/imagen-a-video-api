from flask import Flask, request, render_template_string
import os, base64
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO

app = Flask(__name__)
client = InferenceClient(token=os.getenv("HF_TOKEN"))

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AREPA-VIDEO</title>
<style>
  body{background:#000;color:#0f0;font:20px Arial;text-align:center;padding:20px}
  h1{color:orange;font-size:40px}
  input,button{width:90%;padding:18px;margin:12px;font-size:22px;border-radius:20px}
  input{background:#111;color:#fff;border:3px solid #0f0}
  button{background:#0f0;color:#000;font-weight:bold}
  .bar{height:50px;background:#333;border-radius:25px;overflow:hidden;margin:30px}
  .fill{height:100%;width:0%;background:orange;transition:2s}
  video{max-width:100%;border-radius:25px;margin:30px}
  .dl{background:#0f0;color:#000;padding:18px 40px;border-radius:20px;text-decoration:none;font-size:20px}
</style></head><body>
<h1>AREPA-VIDEO IA</h1>
<p id="msg">¡Sube foto + texto!</p>
<div class="bar"><div class="fill" id="fill"></div></div>

<form method="post" enctype="multipart/form-data" id="form">
  <input type="file" name="f" accept="image/*" required>
  <input type="text" name="t" placeholder="Ej: arepas bailando salsa" required>
  <button>¡VIDEO!</button>
</form>

<div id="result"></div>

<script>
  const form = document.getElementById('form');
  form.onsubmit = async (e) => {
    e.preventDefault();
    const data = new FormData(form);
    document.getElementById('msg').innerText = '10% Subiendo...';
    document.getElementById('fill').style.width = '10%';
    
    const r = await fetch('/', {method:'POST', body:data});
    const html = await r.text();
    document.body.innerHTML = html;
  };
</script>
</body></html>"""

@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "GET":
        return HTML

    # POST
    img = Image.open(request.files["f"].stream).convert("RGB")
    buf = BytesIO(); img.save(buf, "PNG")
    
    video = client.image_to_video(buf.getvalue(), request.form["t"])
    b64 = base64.b64encode(video).decode()

    return f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>body{{background:#000;color:#0f0;text-align:center;padding:20px;font:20px Arial}}
    video{{max-width:100%;border-radius:25px;margin:30px}}
    .dl{{background:#0f0;color:#000;padding:18px 40px;border-radius:20px;text-decoration:none;font-size:22px}}
    </style></head><body>
    <h1 style="color:orange">¡VIDEO LISTO! 🎉</h1>
    <video controls><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video
