import os
from modules.common.imgDict import getImgDict


class BaseTest:
    """测试用例基类，提供通用的初始化逻辑"""

    @classmethod
    def setup_class(cls):
        """类级别初始化，获取图片字典"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(base_dir, "img")
        cls.imgDict = getImgDict(img_dir)
        cls.base_dir = base_dir
        cls.img_dir = img_dir
