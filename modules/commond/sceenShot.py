from airtest.core.api import *
from airtest.aircv.utils import cv2_2_pil
import conf
import os

# 当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 项目根目录，假设你的脚本在 modules/function/commond 目录，项目根目录往上3级
project_root = os.path.abspath(os.path.join(current_dir, '../../'))

def report_screenshot(filename):
    sleep(1)
    screen = G.DEVICE.snapshot()
    pil_img = cv2_2_pil(screen)
    exampleName = conf.load_exampleName()
    outputdir = os.path.join(project_root, "report", "allure-results", exampleName, "img", f"{filename}.jpg")
    pil_img.save(outputdir, quality=10, optimize=True)
    return outputdir
