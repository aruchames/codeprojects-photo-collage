from flask import Flask, request, Response, send_file
from tasks import *
from flask_cors import CORS
from PIL import Image
from celery.result import AsyncResult

from io import BytesIO
import uuid
import codecs

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
        if len(img_ids) == 0:
            return Response("Bad request, please do not send requests without pictures", status=400)
        orientation = request.json["orientation"]
        border = request.json["border"]
        colorstring = str(request.json["color"]).lstrip("#")
        color = tuple(int(colorstring[i:i+2], 16) for i in (0, 2, 4))
        print(color)
        if orientation == "Horizontal":
            result = stitchHorizontal.delay(img_ids, border, color)
        elif orientation == "Vertical":
            result = stitchVertical.delay(img_ids, border, color)
        else:
            return Response("Bad request, must send horizontal or vertical", status=400)
        return result.task_id

    if request.method == 'GET':
        id = request.headers.get("id")
        orientation = request.headers.get("orientation")
        if orientation == "Vertical":
            res = stitchVertical.AsyncResult(id)
        else:
            res = stitchHorizontal.AsyncResult(id)
        if res.ready():
            imgId = res.get()
            return f"results/{imgId}.jpg"
        else:
            return Response("Still Processing", status=202)
