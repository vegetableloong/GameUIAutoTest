import pytest
import re
from modules.commond.connect import *
from modules.commond.sceenShot import *

#自动连接
@pytest.fixture(autouse=True, scope="session")
def connect_devcice():
    androidConnect()


#自动截图，注：所有的类名必须唯一，避免截图出现重复命名
@pytest.fixture(autouse=True, scope="function")
def auto_screenshot(request):
    nodeid = request.node.nodeid  # 格式：test_mm.py::TestRemiEnter::test_enter
    img_name = re.sub(r'.*::(\w+)::(\w+)', r'\1_\2', nodeid)
    print(f"完整用例标识: {img_name}")
    report_screenshot(img_name)

