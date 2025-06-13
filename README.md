# UI自动化测试
基于airtest+pytest二次封装的UI自动化测试工具

# 配置环境
安装python3.9版本
https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe
```
#python安装第三方库airtest
pip install airtest

#python安装第三方库pytest+allure
pip install pytest
pip install pytest-allure
```
安装JavaScript
https://nodejs.org/dist/v22.16.0/node-v22.16.0-x64.msi

# 目录结构
``` |-- /
    |-- modules  
    |   |-- commond                    #通用模块，封装了公共接口
    |   |   |-- connect.py
    |   |   |-- getFunctionName.py
    |   |   |-- imgDict.py
    |   |   |-- sceenShot.py
    |   |   |-- startApp.py
    |   |-- function                   #按功能模块分类，测试用例在该目录编写
    |       |-- login                  #登录测试
    |       |   |-- test_login.py      #按pytest的规则命名，test_开头
    |       |   |-- img                #该模块用例在UI识别需要用到图片都放在img目录
    |       |   |   |-- main_view.png  
    |   |-- sample.py                  #测试用例范例
    |-- report                         #测试报告目录
    |   |-- generateReport.js          #生成单次测试报告脚本
    |   |-- index.html                 #聚合报告首页
    |   |-- process.js
    |   |-- report.js                  #聚合报告脚本
    |   |-- server.js
    |   |-- summary.js
    |   |-- allure-results             #单次测试报告目录
    |   |-- history                    #历史报告，超过指定天数的报告移到历史报告里
    |   |-- public
    |   |-- summary                    #聚合报告数据
    |-- clean.py
    |-- conf.py
    |-- config.json                    #公共配置
    |-- conftest.py                    #pytest公共脚本
    |-- main.py                        
    |-- order.yaml                     #测试用例执行顺序配置
    |-- package-lock.json
    |-- package.json
    |-- pytest.ini                     #pytest配置
    |-- README.md
 ```

# 编写用例

新增用例，需要在modules目录下编写，按照目录结构参照已有的目录结构规范化
```
    |-- modules  
    |   |-- function                  
    |       |-- login                  #模块命名
    |       |   |-- test_login.py      #测试用例集合脚本，按pytest的规则命名，test_开头
    |       |   |-- img                #该模块用例在UI识别需要用到图片都放在img目录
    |       |   |   |-- main_view.png  #图片命名建议规范易读
```
用例集合脚本，可参考sample.py
```
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
class TestSample:  
  
    #增加设备连接用例打印，实际以通过conftest.py执行连接  
    def test_sample(self):  
        print("范例，这里编写具体的测试步骤")
```
# 界面展示
![主界面](/report/public/reportMainView.png "主界面")
![详细报告](/report/public/reportDetailView.png "详细报告")