# test_mm.py
# -*- coding:utf-8 -*-
#控制模块和类的执行顺序用/order.yaml配置，用例类内部的执行顺序自行通过@pytest.mark.order控制
import allure
import os
from airtest.core.api import *
from modules.commond.sceenShot import *
from modules.commond.imgDict import *
from modules.commond.close.closeAllWindows import *

base_dir = os.path.dirname(os.path.abspath(__file__))
#获取相关图片路径
img_dir = os.path.join(base_dir,"img")
imgDict = getImgDict(img_dir)

#注：所有的类名必须唯一
class TestQiuqiuEnter:

    def test_enter(self):
        #进入QIUQIU选关界面
        e = exists(Template(imgDict['qiuqiu_enter']))
        if e:
            click(e)
        else:
            assert False,'找不到QIUQIU入口'


    def test_back(self):
        #返回主界面
        e = exists(Template(imgDict['back']))
        if e:
            click(e)
        else:
            assert False,'找不到返回按钮'
