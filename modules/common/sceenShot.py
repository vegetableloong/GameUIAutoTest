from airtest.core.api import *
from airtest.aircv.utils import cv2_2_pil
import os
import cv2

# 当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 项目根目录，假设你的脚本在 modules/function/commond 目录，项目根目录往上3级
project_root = os.path.abspath(os.path.join(current_dir, '../../'))


def _get_run_id():
    """获取当前运行标识，从环境变量读（由 main.py 启动时设置）

    优先从环境变量读，没有时尝试 config.json 兼容旧用法，
    都没有则用 'unknown'（避免静默失败）。
    """
    env_value = os.environ.get('EXAMPLE_NAME')
    if env_value:
        return env_value
    # 兜底：如果有人单独跑测试没经过 main.py，从 config.json 读一下
    # 这一行在标准流程下不会执行，只是给单跑测试的开发者一个保底
    try:
        import json
        config_path = os.path.join(project_root, "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f).get("exampleName", "unknown")
    except Exception:
        return "unknown"


def report_screenshot(filename):
    sleep(1)
    screen = G.DEVICE.snapshot()
    pil_img = cv2_2_pil(screen)
    exampleName = _get_run_id()
    outputdir = os.path.join(project_root, "report", "allure-results", exampleName, "img", f"{filename}.jpg")
    pil_img.save(outputdir, quality=10, optimize=True)
    return outputdir