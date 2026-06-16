# UI自动化测试

基于 Airtest + Pytest 二次封装的 UI 自动化测试工具，支持 Android 应用自动化测试。

## 功能特性

- **UI 自动化测试**：基于 Airtest 框架，支持图片识别和坐标操作
- **多级 fallback 设备连接**：adb devices 列表 → 常见模拟器端口（夜神/雷电/BlueStacks/MuMu/MEmu/AVD/WSA）
- **登录优先策略**：登录失败立即终止整轮测试，避免后续用例空跑
- **测试报告系统**：自研 Web 报告（Express + Chart.js），聚合报告 Dashboard + 单次详细报告
- **失败用例统计**：自动统计 Top10 高频失败用例
- **OCR 数值校验**：RapidOCR 单例 + K/M/B 单位换算
- **报告过期清理**：自动归档 30 天前的旧报告

## 快速开始

### 环境要求

| 工具 | 版本 | 用途 |
|---|---|---|
| Python | 3.9+ | 跑测试用例 |
| Node.js | 14+ | 跑报告服务 |
| Allure CLI | 2.13+ | 生成 Allure HTML 报告 |
| ADB | 最新 | 连接 Android 设备 |

### 安装依赖

```bash
# 1. 克隆项目
git clone <repo>
cd GameUIAutoTest-master

# 2. 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. 安装 Python 核心依赖
pip install -r requirements.txt

# 4.（可选）安装 OCR 依赖 —— 仅在做金币等数值校验时需要
pip install rapidocr-onnxruntime

# 5. 安装 Node 依赖（报告服务）
cd report
npm install
cd ..
```

### 系统工具安装

如果上一步报 `command not found`，按系统装：

```bash
# macOS
brew install allure node android-platform-tools

# Windows (scoop)
scoop install allure node adb

# 通用：Node.js 也可以直接从 https://nodejs.org/ 下载安装包
```

### 运行测试

```bash
# 完整流程：连接设备 → 登录 → 跑其它用例 → 生成报告
python main.py

# 只跑登录用例
pytest -s -x --alluredir=./report/allure-results/login/json ./modules/function/login/test_login.py

# 跑指定模块
pytest -s --maxfail=3 --alluredir=./report/allure-results/json modules/function/<module>/

# 跑单个测试方法
pytest -s modules/function/login/test_login.py::TestLogin::test_login_flow
```

### 查看报告

跑完测试后服务会自动保持运行（端口 8090），也可手动启动：

```bash
# 方式一：跑测试时自动启动（推荐）
python main.py

# 方式二：手动启动报告服务
cd report
node server.js

# 方式三：通过管理脚本（带启动检测 + 日志 + 旧进程清理）
python report_server.py            # 启动
python report_server.py --stop     # 停止
```

访问：

- 聚合报告 Dashboard: <http://127.0.0.1:8090>
- 单次详细报告: <http://127.0.0.1:8090/detail.html?name=<14位时间戳>>

## 目录结构

```
|-- /
    |-- main.py                        # 主入口，编排整个测试流程
    |-- report_server.py               # 报告服务管理（启动检测 + 日志转发 + 旧进程清理）
    |-- conf.py                        # 静态配置管理（包名、时间戳）
    |-- clean.py                       # 归档 30 天前的旧报告
    |-- conftest.py                    # pytest 全局 fixture
    |-- config.json                    # 运行时配置（包名）
    |-- order.yaml                     # 用例执行顺序配置
    |-- requirements.txt               # Python 依赖清单
    |-- pytest.ini                     # pytest 配置
    |
    |-- modules/
    |   |-- common/                    # 公共封装层
    |   |   |-- connect.py             # 多级 fallback 设备连接
    |   |   |-- functionAPI.py         # 图片点击/等待/查找
    |   |   |-- sceenShot.py           # 自动截图到报告目录
    |   |   |-- startApp.py            # 通过 package 字段重启 App
    |   |   |-- imgDict.py             # 扫描 img/ 目录成字典
    |   |   |-- checkData.py           # OCR + 单位换算（K/M/B）
    |   |   |-- getFunctionName.py     # 反射获取调用方名
    |   |   |-- base_test.py           # 测试基类
    |   |   |-- close/closeAllWindows.py   # 循环点击关闭弹窗
    |   |   |-- ocr/rapidOCR.py        # RapidOCR 多版本输出兼容
    |   |
    |   |-- function/                  # 业务用例层
    |       |-- conftest.py            # 提供 img_dict fixture
    |       |-- login/                 # 登录模块
    |       |   |-- test_login.py
    |       |   |-- img/               # UI 识别图片
    |
    |-- report/                        # 自研 Web 报告系统
    |   |-- server.js                  # Express 服务（端口 8090）
    |   |-- index.html                 # 聚合报告 Dashboard
    |   |-- detail.html                # 单次详细报告
    |   |-- report.js                  # Dashboard 逻辑（Chart.js）
    |   |-- generateReport.js          # 单次报告生成器
    |   |-- summary.js                 # 扫描 allure-results 生成 summary
    |   |-- process.js                 # summary.json 统计逻辑
    |   |-- refreshGenerate.py         # 批量重新生成历史报告
    |   |-- allure-results/            # 单次测试结果（按 14 位时间戳分子目录）
    |   |-- summary/                   # 聚合报告数据
    |   |-- history/                   # 30 天前归档目录
```

## 编写测试用例

### 新增模块

在 `modules/function/` 下创建新目录：

```
modules/
└── function/
    └── new_module/
        ├── test_newmodule.py   # 测试用例集合
        └── img/                # UI 识别图片
            └── button.png
```

### 用例模板

```python
# test_example.py
# -*- coding:utf-8 -*-
import allure
from airtest.core.api import *
from modules.common.sceenShot import *
from modules.common.imgDict import *

class TestExample:

    @allure.step("执行测试步骤")
    def test_example(self):
        """测试用例示例"""
        # 截图
        auto_screenshot("步骤描述")

        # 点击图片
        click_img("button.png", "点击失败")

        # 等待图片出现
        wait_img("loading.png")

        # 检查图片是否存在
        exists_img("success.png", "未找到成功页面")
```

## 报告说明

### 聚合报告 (index.html)

![聚合报告1](/report/public/reportMainView1.png)
![聚合报告2](/report/public/reportMainView2.png)

### 详细报告 (detail.html)

![详细报告](/report/public/reportDetailView1.png)

## 配置说明

### config.json

```json
{
  "package": "com.example.app"
}
```

`exampleName`（本次运行的时间戳）由 `main.py` 启动时自动生成，通过环境变量 `EXAMPLE_NAME` 传递给子进程，不再写死在配置文件里。

### order.yaml

控制用例执行顺序：

```yaml
- modules.function.login.test_login.TestLogin
```
