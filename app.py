from flask import Flask, request
import os, base64
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO

app = Flask(__name__)
client = InferenceClient()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return '''
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>AREPA-VIDEO</title>
        <style>
          body{font:20px Arial;text-align:center;background:#000;color:#0f0;padding:20px}
          h1{color:orange;font-size:40px}
          input,button{width:90%;padding:20px;margin:15px;font-size:22px;border-radius:20px}
          input{background:#111;color:#fff;border:3px solid #0f0}
          button{background:#0f0;color:#000;font-weight:bold}
          .bar{height:50px;background:#333;border-radius:25px;overflow:hidden;margin:30px}
          .fill{height:100%;width:0%;background:orange;transition:2s}
        </style>
        <h1>AREPA-VIDEO IA</h1>
        <p id="m">¡Sube foto + texto!</p>
        <div class="bar"><div class="fill" id="f"></div></div>
        <form id="form" enctype="multipart/form-data">
          <input type=file name=f accept="image/*" required>
          <input type=text name=t placeholder="Ej: arepas bailando" required>
          <button>¡VIDEO!</button>
        </form>
        <script>
          document.getElementById('form').onsubmit = async e => {
            e.preventDefault();
            let d = new FormData(e.target);
            m.innerText = "10% Subiendo..."; f.style.width = "10%";
            let r = await fetch("/", {method:"POST", body:d});
            document.body.innerHTML = await r.text();
          };
        </script>
        '''

    # POST → GENERA VIDEO
    img = Image.open(request.files["f"].stream).convert("RGB")
    buf = BytesIO(); img.save(buf, "PNG")
    video = client.image_to_video(buf.getvalue(), request.form["t"])
    b64 = base64.b64encode(video).decode()

    return f'''
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
      body{{background:#000;color:#0f0;text-align:center;padding:20px;font:20px Arial}}
      video{{max-width:100%;border-radius:25px;margin:30px}}
      a{{background:#0f0;color:#000;padding:20px 50px;border-radius:20px;text-decoration:none;font-size:24px}}
    </style>
    <h1 style="color:orange">¡VIDEO LISTO! 🎉</h1>
    <video controls><source src="data:video/mp4;base64,{b64}"></video><br>
    <a href="data:video/mp4;base64,{b64}" download="arepa.mp4">DESCARGAR</a>
    <br><br><a href="/">← OTRO VIDEO</a>
    '''

# Render necesita esta línea
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
