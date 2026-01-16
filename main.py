import pytest
from airtest.core.api import *
from datetime import datetime
import os
import subprocess
import conf
import logging
import yaml
import clean

import warnings
warnings.filterwarnings("ignore", category=UserWarning)


if __name__ == '__main__':
    # 打开聚合报告
    print("启动聚合报告")
    subprocess.Popen(["node", "./report/server.js"])

    #存用例名称公用
    conf.save_exampleName()
    exampleName = conf.load_exampleName()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    #创建allure报告路径
    json_dir = base_dir + "./report/allure-results/" + exampleName + "/json"
    html_dir = base_dir + "./report/allure-results/" + exampleName + "/html"
    img_dir = base_dir + "./report/allure-results/" + exampleName + "/img"
    log_dir = base_dir + "./report/allure-results/" + exampleName + "/log"
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(html_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    # 设置日志配置
    logging.basicConfig(
        filename=log_dir + "/execution.log",  # 指定日志文件名
        level=logging.DEBUG,  # 设置日志级别（INFO、DEBUG、WARNING等）
        format='%(asctime)s - %(levelname)s - %(message)s'  # 设置日志输出格式
    )

    # 第一次只跑登录
    # 报错直接停止后续用例
    login_case = "modules/function/login/test_login.py"
    login_args = ["-s", "-x", "--alluredir=" + json_dir, "--clean-alluredir", login_case]
    result = pytest.main(login_args)

    #执行pytest用例，新增用例记得添加order.yaml配置
    #pytest.main(["-s", "--alluredir=" + json_dir])
    #--maxfail=3 表示允许最多 3 个失败后停止。
    if result == 0:
        with open("order.yaml", "r", encoding='utf-8') as f:
            cases = yaml.safe_load(f)
            args = ["-s", "--maxfail=3", "--alluredir=" + json_dir] + cases
            pytest.main(args)


    # 将测试报告转为html格式
    split = 'allure ' + 'generate ' + json_dir + ' -o ' + html_dir + ' --clean'
    os.system(split)

    # 清理报告，超过30天的报告移到history里
    clean.backup()

    # 生成单独报告
    subprocess.run(["node", "./report/generateReport.js", exampleName])

    # 更新聚合报告数据
    subprocess.run(["node", "./report/summary.js"])







