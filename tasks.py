from celery import Celery
from PIL import Image
import uuid

app = Celery('tasks', backend='rpc://', broker='pyamqp://')


def findDimensions(img_ids, orientation):
    images, staticDimension = [], 0
    staticDimensionIndex = 0 if orientation == "Vertical" else 1

    for id in img_ids:
        image = Image.open(f"pics/{id}.jpg")
        print(f"Adding image {id}")
        staticDimension += image.size[staticDimensionIndex]
        images.append(image)

    staticDimension //= len(img_ids)

    variableDimensions = []
    for img in images:
        width, height = image.size
        multiplier = height / width if orientation == "Vertical" else width / height
        newDimension = int(staticDimension * multiplier)
        variableDimensions.append(newDimension)

    return staticDimension, variableDimensions, images


def getDynamicTotalDimension(border, dynamicDimensions):
    n = len(dynamicDimensions)
    return (n + 1) * border + sum(dynamicDimensions)


def getStaticTotalDimenison(border, staticDimension):
    return 2 * border + staticDimension


@app.task
def stitchVertical(img_ids, border, color):
    print(
        f"Received request: imageIds: {img_ids}, border: {border}, color: {color}")
    newWidth, newHeights, images = findDimensions(img_ids, "Vertical")

    totalWidth = getStaticTotalDimenison(border, newWidth)
    totalHeight = getDynamicTotalDimension(border, newHeights)
    newSize = (totalWidth, totalHeight)

    result = Image.new("RGB", newSize, (color[0], color[1], color[2]))
    xPos, yPos = border, border
    for i, img in enumerate(images):
        print(img.filename)
        resized = img.resize((newWidth, newHeights[i]))
        result.paste(resized, (xPos, yPos))
        yPos += resized.height + border

    id = uuid.uuid4()
    result.save(f"frontend/results/{id}.jpg")
    return id


@app.task
def stitchHorizontal(img_ids, border, color):
    newHeight, newWidths, images = findDimensions(img_ids, "Horizontal")

    totalWidth = getDynamicTotalDimension(border, newWidths)
    totalHeight = getStaticTotalDimenison(border, newHeight)
    newSize = (totalWidth, totalHeight)

    result = Image.new("RGB", newSize, (color[0], color[1], color[2]))
    xPos, yPos = border, border
    for i, img in enumerate(images):
        resized = img.resize((newWidths[i], newHeight))
        result.paste(resized, (xPos, yPos))
        xPos += resized.width + border

    id = uuid.uuid4()
    result.save(f"frontend/results/{id}.jpg")
    return id
