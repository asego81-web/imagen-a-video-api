from flask import Flask, request, render_template_string
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO
import base64
import os

app = Flask(__name__)
client = InferenceClient(token=os.getenv("HF_TOKEN"))

HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device=device-width, initial-scale=1.0">
  <title>Video IA Móvil</title>
  <style>
    body { background:#000; color:#fff; padding:20px; text-align:center; font-family:Arial; }
    h1 { font-size:24px; background:linear-gradient(90deg,#00ff88,#ff00aa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .upload { border:2px dashed #444; padding:40px; border-radius:16px; margin:20px 0; background:#111; }
    input, button { width:100%; padding:16px; margin:8px 0; border-radius:12px; font-size:18px; }
    input { background:#222; color:#fff; border:none; }
    button { background:linear-gradient(45deg,#00ff88,#ff00aa); color:#000; border:none; font-weight:bold; }
    video { width:100%; max-width:400px; border-radius:16px; margin:20px 0; }
    .download { background:#10b981; color:#fff; padding:12px 20px; border-radius:12px; text-decoration:none; }
  </style>
</head>
<body>
  <h1>VIDEO IA MÓVIL</h1>
  <p>Sube foto + texto → Video mágico</p>
  <form method="post" enctype="multipart/form-data">
    <div class="upload">
      <input type="file" name="image" accept="image/*" required>
    </div>
    <input type="text" name="prompt" placeholder="Ej: haz que baile flamenco en la luna" required>
    <button>Generar Video</button>
  </form>
  {% if video_url %}
    <video controls>
      <source src="{{ video_url }}" type="video/mp4">
    </video>
    <br>
    <a href="{{ video_url }}" download="video-ia.mp4" class="download">DESCARGAR</a>
  {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    video_url = None
    if request.method == 'POST':
        file = request.files['image']
        prompt = request.form['prompt']
        try:
            img = Image.open(file.stream).convert("RGB")
            img_byte = BytesIO()
            img.save(img_byte, format="PNG")
            img_byte = img_byte.getvalue()
            video_bytes = client.image_to_video(
                image=img_byte,
                prompt=prompt,
                model="stabilityai/stable-video-diffusion-img2vid-xt",
                num_inference_steps=25
            )
            video_b64 = base64.b64encode(video_bytes).decode()
            video_url = f"data:video/mp4;base64,{video_b64}"
        except Exception as e:
            return render_template_string(HTML, error=str(e))
    return render_template_string(HTML, video_url=video_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
