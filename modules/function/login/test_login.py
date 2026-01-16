# test_mm.py
# -*- coding:utf-8 -*-
#控制模块和类的执行顺序用/order.yaml配置，用例类内部的执行顺序自行通过@pytest.mark.order控制

from modules.common.close.closeAllWindows import *
from modules.common.startApp import *
from modules.common.functionAPI import *

base_dir = os.path.dirname(os.path.abspath(__file__))
#获取相关图片路径
img_dir = os.path.join(base_dir,"img")
imgDict = getImgDict(img_dir)

userName = "cjp042"
passWord = "123456"

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

    # 进入内网服务器
    def test_enterInnerService(self):
        exists_and_click(imgDict['inner_service'],"不在选服界面")

    # 判断在不在登录界面
    def test_waitLoginMain(self):
        imgList = [imgDict['login_main_page'],imgDict['login_main_page2']]
        wait_img_list(imgList)

    # 点击登录游戏
    def test_usernameLogin(self):
        exists_and_click_noerr(imgDict['choice_username_login'])
        exists_and_click_noerr(imgDict['choice_username_login2'])

    def test_waitUernameLogin(self):
        exists_img(imgDict['login_main_page2'],"找不到账号密码输入界面")

    def test_enterUsernamePwd(self):
        click_img_pos(imgDict['username'],30,0)
        text(userName)
        click_img_pos(imgDict['password'],30,0)
        text(passWord)
        click_img(imgDict['certain_login'])

    #关闭弹窗
    def test_closeWindows(self):
        #尝试关闭所有弹窗
        closeWindows()

    # 判断在不在主界面
    def test_isInMain(self):
        imgList = [imgDict['main_view'], imgDict['main_view2']]
        exists_img_list(imgList,"不在主界面")

