# test_mm.py
# -*- coding:utf-8 -*-
#控制模块和类的执行顺序用/order.yaml配置，用例类内部的执行顺序自行通过@pytest.mark.order控制

from modules.commond.close.closeAllWindows import *
from modules.commond.existsClick import *

base_dir = os.path.dirname(os.path.abspath(__file__))
#获取相关图片路径
img_dir = os.path.join(base_dir,"img")
imgDict = getImgDict(img_dir)

#注：所有的类名必须唯一
class TestSample:

    #增加设备连接用例打印，实际以通过conftest.py执行连接
    def test_sample(self):
        print("范例，这里编写具体的测试步骤")


