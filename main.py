from flask import Flask, request, make_response, send_file
import os
from PIL import Image
from io import BytesIO
import numpy as np

app = Flask(__name__)

@app.route('/', methods=['POST'])
def segment():
    # Pillowに変換 
    img = Image.open(BytesIO(request.data)).convert('RGB')
    #色の抽出
    small_img = img.resize((100,200))
    color_arr = np.array(small_img)
    w_size, h_size, n_color = color_arr.shape
    color_arr = color_arr.reshape(w_size * h_size, n_color)
    r = [elem[0] for elem in color_arr]
    g = [elem[1] for elem in color_arr]
    b = [elem[2] for elem in color_arr]

    def expand(pil_img):
      background_color = (int(np.median(r)), int(np.median(g)), int(np.median(b)))
      width, height = pil_img.size
      if width == height:
          return pil_img
      elif width > height:
          result = Image.new(pil_img.mode, (width, width), background_color)
          result.paste(pil_img, (0, (width - height) // 2))
          return result
      else:
          result = Image.new(pil_img.mode, (height, height), background_color)
          result.paste(pil_img, ((height - width) // 2, 0))
          return result

    ret_img = expand(img)

    img_io = BytesIO()
    ret_img.save(img_io, 'PNG', quality=95)
    img_io.seek(0)

    response = make_response(send_file(img_io, mimetype='image/png'))
    return response
    
app.run(host='0.0.0.0', port=8080)
