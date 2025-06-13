# test_mm.py
# -*- coding:utf-8 -*-
#控制模块和类的执行顺序用/order.yaml配置，用例类内部的执行顺序自行通过@pytest.mark.order控制
import allure
import os
from airtest.core.api import *
from modules.commond.sceenShot import *
from modules.commond.imgDict import *
from modules.commond.close.closeAllWindows import *
from modules.commond.startApp import *

base_dir = os.path.dirname(os.path.abspath(__file__))
#获取相关图片路径
img_dir = os.path.join(base_dir,"img")
imgDict = getImgDict(img_dir)

#注：所有的类名必须唯一
class TestLogin:

    #增加设备连接用例打印，实际以通过conftest.py执行连接
    def test_connect(self):
        print("连接设备")

    #启动应用
    def test_appstart(self):
        startApp()
        #判断应用是否启动
        running = shell(f"pidof {package_name}")
        assert running.strip(), f"App {package_name} 未能启动"

    #关闭弹窗
    def test_closeWindows(self):
        #尝试关闭所有弹窗
        closeWindows()

    # 判断在不在主界面
    def test_isInMain(self):
        e = exists(Template(imgDict['main_view']))
        assert e,"不在主界面"

