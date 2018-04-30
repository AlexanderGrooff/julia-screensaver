import os.path
from cmath import pi, exp
from multiprocessing import Pool
import numpy as np
from PIL import Image
import argparse

screenSizeX = 1920
screenSizeY = 1080

# Julia parameters
minX = -1.5
maxX = 1.5
minY = -1.2
maxY = 1.2
max_iteration = 500
res = 1

# PIL accesses images in Cartesian co-ordinates, so it is Image[columns, rows]
img = Image.new('RGB', (250,250), "black") # create a new black image
pixels = img.load() # create the pixel map

def pixelToJulia(pixelX, pixelY, c):
    zx, zy = scalePixel(pixelX, pixelY)
    iteration = 0

    while zx * zx + zy * zy < 4 and iteration < max_iteration:
        xtemp = zx * zx - zy * zy
        zy = 2 * zx * zy + c.imag
        zx = xtemp + c.real
        iteration += 1
    
    return iteration

# Scale from pixel coords to the coord plane for complex numbers
def scalePixel(pixelX, pixelY):
    x = minX + (pixelX / screenSizeX) * (maxX - minX)
    y = minY + (pixelY / screenSizeY) * (maxY - minY)
    return [x, y]

# Color scale
def iterationsToColor(it):
    # scaledIt = it * 255 / max_iteration
    red = it * 3
    green = it * 3
    blue = it * 3

    return ((int)(red), (int)(green), (int)(blue))

# Return complex rotation constant with given angle
def rotateC(rotation):
    return 0.7885 * exp(complex(0, rotation)) 


def drawImage(imgNrAndConst, path=None):
    # Get arguments from tuple
    (imgNr, rotation) = imgNrAndConst

    imagePath = path or "./img/bw-1280x1024/r_" + str(imgNr) + ".png"

    # Don't create a new image if it already exists
    if os.path.exists(imagePath):
        return

    # Turn rotation to constant
    c = rotateC(rotation)
    image = Image.new("RGB", (screenSizeX, screenSizeY), "white")
    pixels = image.load()

    # Calculate the number of iterations for every pixel on the screen
    for x in range(0, screenSizeX, res):
        for y in range(0, screenSizeY, res):
            iterations = pixelToJulia(x, y, c)
            pixels[x, y] = iterationsToColor(iterations)

    print(imgNr, rotation)
    image.save(imagePath, 'png')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frame", help="Only generate the given frame", type=int)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if args.frame:
        rotation = (args.frame / 1024) * 2 * pi 
        drawImage([args.frame, rotation], "frame{}.png".format(args.frame))
    else:
        # Multithread to 16 cores
        with Pool(16) as pool:
            # All angles from 0 to 2pi with pi/512 step intervals
            pool.map(drawImage, enumerate(np.arange(0, 2 * pi, pi / 512)))
