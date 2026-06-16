import pytest
from airtest.core.api import *
import os
import subprocess
import logging
import yaml
import clean
import report_server
from conf import make_example_name, EXAMPLE_NAME_ENV

import warnings
warnings.filterwarnings("ignore", category=UserWarning)


if __name__ == '__main__':
    # 生成本次运行的唯一标识，同时写入环境变量让子进程（包括 pytest 用例）可见
    exampleName = make_example_name()
    os.environ[EXAMPLE_NAME_ENV] = exampleName

    base_dir = os.path.dirname(os.path.abspath(__file__))

    #创建allure报告路径
    json_dir = os.path.join(base_dir, "report", "allure-results", exampleName, "json")
    html_dir = os.path.join(base_dir, "report", "allure-results", exampleName, "html")
    img_dir = os.path.join(base_dir, "report", "allure-results", exampleName, "img")
    log_dir = os.path.join(base_dir, "report", "allure-results", exampleName, "log")
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(html_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    # 设置日志配置
    logging.basicConfig(
        filename=os.path.join(log_dir, "execution.log"),
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 启动报告服务（带启动检测 + 日志转发 + 旧进程清理）
    # 启动失败不会中断测试，只是不方便查看报告
    server_process = None
    try:
        server_process = report_server.start_server(log_dir=log_dir)
    except RuntimeError as e:
        print(f"\n⚠️  报告服务启动失败: {e}")
        print("    测试将继续，但可能无法查看报告\n")

    # 第一次只跑登录
    # 报错直接停止后续用例
    login_case = "modules/function/login/test_login.py"
    login_args = ["-s", "-x", "--alluredir", json_dir, "--clean-alluredir", login_case]
    result = pytest.main(login_args)

    #执行pytest用例，新增用例记得添加order.yaml配置
    #--maxfail=3 表示允许最多 3 个失败后停止。
    if result == 0:
        with open("order.yaml", "r", encoding='utf-8') as f:
            cases = yaml.safe_load(f) or []
        args = ["-s", "--maxfail=3", "--alluredir", json_dir] + cases
        pytest.main(args)


    # 将测试报告转为html格式
    try:
        print(f"\n生成 Allure HTML 报告: {json_dir} -> {html_dir}")
        subprocess.run(
            ["allure", "generate", json_dir, "-o", html_dir, "--clean"],
            check=True
        )
    except FileNotFoundError:
        print("⚠️  未找到 allure 命令，跳过 HTML 报告生成")
        print("    安装方法：pip install allure-pytest，并配置 allure 命令行工具")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Allure 报告生成失败: {e}")

    # 清理报告，超过30天的报告移到history里
    clean.backup()

    # 生成单独报告
    try:
        subprocess.run(
            ["node", "./report/generateReport.js", exampleName],
            check=True, timeout=60
        )
    except subprocess.CalledProcessError as e:
        print(f"⚠️  单次报告生成失败: {e}")
    except subprocess.TimeoutExpired:
        print("⚠️  单次报告生成超时（60s）")

    # 更新聚合报告数据
    try:
        subprocess.run(
            ["node", "./report/summary.js"],
            check=True, timeout=60
        )
    except subprocess.CalledProcessError as e:
        print(f"⚠️  聚合数据更新失败: {e}")
    except subprocess.TimeoutExpired:
        print("⚠️  聚合数据更新超时（60s）")

    # 报告服务保持运行，用户可继续浏览
    # 如需停止：运行 `python report_server.py --stop` 或直接结束 node 进程
    if server_process is not None:
        print(f"\n📊  报告服务运行中 (PID {server_process.pid})")
        print(f"    访问: http://127.0.0.1:{report_server.DEFAULT_PORT}/")
        print(f"    停止: python report_server.py --stop")







