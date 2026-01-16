import json
import os
from airtest.core.api import *

base_dir = os.path.dirname(os.path.abspath(__file__))
#获取包名配置
json_path = os.path.abspath(os.path.join(base_dir, "..", "..", "config.json"))
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
package_name = data.get("package")

def startApp():
    stop_app(package_name)
    start_app(package_name)
    sleep(20)
