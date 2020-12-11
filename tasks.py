from celery import Celery
from PIL import Image

app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task
def stitchVertical(img_ids):
    for id in img_ids:
        image = Image.open(f"pics/{id}.jpg")
        print(image.format, image.mode, image.size, image.palette)
