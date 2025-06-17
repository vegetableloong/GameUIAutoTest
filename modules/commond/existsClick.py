from airtest.core.api import *


#封装airtest，点击图片,默认点击1次
def click_img(imgPath,times=1):
    click(Template(imgPath),times)

#封装airtest，存在图片，加上自定义错误信息
def exists_img(imgPath,error_msg):
    e = exists(Template(imgPath))
    assert e, error_msg

#封装airtest，存在图片并点击，加上自定义错误信息
def exists_and_click(imgPath,error_msg):
    e = exists(Template(imgPath))
    if e:
        click_img(imgPath)
    else:
        assert e, error_msg