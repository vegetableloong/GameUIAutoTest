from airtest.core.api import *
import os
from modules.common.connect import *
from modules.common.imgDict import *

base_dir = os.path.dirname(os.path.abspath(__file__))
close_dir = os.path.join(base_dir,"closeAllWindows")

def closeWindows():
    while True:  # 使用无限循环，直到没有图片可以点击
        found = False  # 标记是否找到图片并执行点击

        # 遍历目录下所有图片
        for img in os.listdir(close_dir):
            imgPath = os.path.join(close_dir, img)

            if os.path.exists(imgPath):  # 确保文件存在
                if exists(Template(imgPath)):  # locateOnScreen 用来检查图片是否存在
                    print(f"图片找到并点击: {imgPath}")
                    click(Template(imgPath))
                    found = True  # 找到并点击，标记为 True

        if not found:
            print("没有找到可点击的图片，退出循环。")
            break  # 如果没有找到图片，退出循环