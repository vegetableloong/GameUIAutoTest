import cv2
from typing import List, Optional, Tuple, Any
from airtest.core.api import *
from modules.common.checkData import *


#封装airtest，点击图片,默认点击1次
def click_img(imgPath: str, times: int = 1) -> None:
    """点击图片"""
    click(Template(imgPath), times)


#封装airtest，点击图片+坐标偏移,默认点击1次
def click_img_pos(imgPath: str, posX: int, posY: int, times: int = 1) -> None:
    """点击图片并偏移坐标"""
    pos = exists(Template(imgPath))
    poslist = [pos[0], pos[1]]
    poslist[0] += posX
    poslist[1] += posY
    click(poslist, times)


#封装airtest，存在图片，加上自定义错误信息
def exists_img(imgPath: str, error_msg: str) -> bool:
    """检查图片是否存在，不存在则抛出AssertionError"""
    e = exists(Template(imgPath))
    assert e, error_msg
    return True


#封装airtest，存在图片列表中任意一张则返回成功，加上自定义错误信息
def exists_img_list(imgList: List[str], error_msg: str) -> bool:
    """检查图片列表中是否有任意一张存在"""
    bool_img = False
    for imgPath in imgList:
        e = exists(Template(imgPath))
        if e:
            bool_img = True
            break
    if bool_img:
        return True
    else:
        assert False, error_msg


#封装airtest，存在图片并点击，加上自定义错误信息
def exists_and_click(imgPath: str, error_msg: str) -> None:
    """检查图片是否存在，存在则点击，否则抛出AssertionError"""
    e = exists(Template(imgPath))
    if e:
        click_img(imgPath)
    else:
        assert e, error_msg


#封装airtest，存在图片并点击，不存在就跳过不报错
def exists_and_click_noerr(imgPath: str) -> bool:
    """检查图片是否存在，存在则点击，不报错"""
    e = exists(Template(imgPath))
    if e:
        click_img(imgPath)
        return True
    return False


#封装airtest，存在图片并点击，加上坐标偏移
def exists_and_click_with_offset(imgPath: str, posX: int, posY: int, error_msg: str) -> None:
    """检查图片是否存在，存在则点击并偏移坐标，否则抛出AssertionError"""
    e = exists(Template(imgPath))
    if e:
        click_img_pos(imgPath, posX, posY)
    else:
        assert e, error_msg


#封装airtest，等待界面出现
def wait_img(imgPath: str, timeout: int = 20, interval: int = 1) -> Optional[Tuple[int, int]]:
    """等待图片出现，返回坐标或None"""
    w = wait(Template(imgPath), timeout=timeout, interval=interval)
    if w:
        return w
    return None


#封装airtest，等待界面出现，存在任意图像就判断成功
def wait_img_list(imgList: List[str], timeout: int = 20, interval: int = 1) -> Optional[str]:
    """等待图片列表中任意一张出现，返回匹配的路径或None"""
    for imgPath in imgList:
        print(imgPath)
        w = wait(Template(imgPath), timeout=timeout, interval=interval)
        if w:
            return imgPath
    return None


#封装airtest，find_all查找界面所有相同元素的图片
def find_all_img(imgPath: str) -> Optional[List[dict]]:
    """查找界面所有匹配的图片"""
    f = find_all(Template(imgPath))
    return f


#截图指定坐标图片保存文件，filename保存路径，region坐标xy长宽wh=(x, y, w, h)
def catch_screenshot(filename: str, region: Tuple[int, int, int, int]) -> str:
    """截图指定区域并保存"""
    screen = device().snapshot()  # numpy array
    x, y, w, h = region
    crop = screen[y: y + h, x: x + w]
    cv2.imwrite(filename, crop)
    return filename


#截图金币的数值，并ocr文本识别转换
def get_coin_data(imgpth: str, output: str) -> float:
    """获取金币数值并返回浮点数"""
    pos = [0, 0]
    findImg = find_all_img(imgpth)
    if findImg:
        tmp = [0, 0]
        for pos_result in findImg:
            if pos_result['result'][1] > tmp[1]:
                tmp[0] = pos_result['result'][0]
                tmp[1] = pos_result['result'][1]
        pos[0] = tmp[0] + 20
        pos[1] = tmp[1] - 20
    if pos[0] != 0 and pos[1] != 0:
        catch_region = (pos[0], pos[1], 85, 40)
        catch_imgpath = output
        catch_screenshot(catch_imgpath, catch_region)

    data = img_coin_ocr(catch_imgpath)

    return data
