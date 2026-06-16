from airtest.core.api import *
import os

imgDict = {}

def getImgDict(imgDir):
    for img in os.listdir(imgDir):
        name, extension  = os.path.splitext(img)
        imgPath = os.path.join(imgDir, img)
        imgDict[name] = imgPath

    return imgDict
