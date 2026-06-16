import os
from airtest.core.api import *
from conf import get_package

# 启动时即读取包名（避免每次调用 startApp() 时重复 IO）
package_name = get_package()


def startApp():
    stop_app(package_name)
    start_app(package_name)
    sleep(20)
