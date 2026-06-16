import os
import pytest
from modules.common.imgDict import getImgDict


@pytest.fixture(scope="class")
def img_dict():
    """提供图片字典 fixture"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, "img")
    return getImgDict(img_dir)
