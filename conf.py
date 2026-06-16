"""
静态配置管理：负责加载 config.json 中**不变**的配置项（包名等）。

运行时状态（如本次运行的 exampleName 时间戳）通过环境变量传递，
见 main.py 和 modules/common/sceenShot.py。
"""
import json
import os
from datetime import datetime

# 配置文件路径：项目根目录的 config.json
_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "config.json"
)

# exampleName 的格式契约（YYYYMMDDHHMMSS，14 位纯数字）
# 报告目录命名、report/summary.js 扫描、Node 脚本都依赖此格式
EXAMPLE_NAME_FORMAT = "%Y%m%d%H%M%S"
EXAMPLE_NAME_ENV = "EXAMPLE_NAME"


def _load_config() -> dict:
    """读取 config.json 全部内容"""
    if not os.path.exists(_CONFIG_PATH):
        raise FileNotFoundError(
            f"配置文件不存在: {_CONFIG_PATH}\n"
            f"请创建 config.json，至少包含 {{\"package\": \"<包名>\"}}"
        )
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_package() -> str:
    """获取 Android 包名（被 startApp.py 使用）"""
    return _load_config().get("package", "")


def make_example_name(timestamp: datetime = None) -> str:
    """
    生成 exampleName 时间戳字符串。

    所有需要生成运行标识的地方都应通过此函数，避免散落的 strftime 写法导致
    格式不一致（Node 脚本 / summary.js 扫描等都依赖此格式）。

    :param timestamp: 可选，传入则格式化该时间；不传则用当前时间
    :return: 14 位时间字符串，如 "20260616174057"
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(EXAMPLE_NAME_FORMAT)


# 保留 _CONFIG_PATH 供外部模块（如 sceenShot.py 兼容旧用法）使用
__all__ = ["get_package", "make_example_name", "EXAMPLE_NAME_FORMAT", "EXAMPLE_NAME_ENV", "_CONFIG_PATH"]
