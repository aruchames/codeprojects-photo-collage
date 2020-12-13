from flask import Flask, request, Response, send_file
from tasks import stitchVertical
from flask_cors import CORS
from PIL import Image

from io import BytesIO
import uuid

app = Flask(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/images', methods=['POST', 'GET'])
def handle_image():
    if request.method == 'POST':
        imageContents = request.data

        im = Image.open(BytesIO(imageContents))
        id = uuid.uuid4()
        im.save(f"pics/{id}.jpg")
        return str(id)
    else:
        return "hello"


@app.route('/stitch', methods=['POST', 'GET'])
def stitch():
    if request.method == 'POST':
        img_ids = request.json["ids"]
        orientation = request.json["orientation"]

        if orientation == "Horizontal":
            return "not implemented - horizontal stitch"
        elif orientation == "Vertical":
            result = stitchVertical.delay(img_ids)
            return result.task_id

    if request.method == 'GET':
        id = request.json["id"]
        res = AsyncResult(id)
        if res.ready():
            finalImage = res.get()
            return send_file(finalImage, mimetype='image/jpg')
        else:
            return Response("Still Processing", status=202)
