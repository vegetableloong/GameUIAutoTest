# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

**基于 Airtest + Pytest 二次封装的 Android 游戏 UI 自动化测试框架**，配套自研 Web 报告系统（Express + Chart.js）。

核心特点：
- **图像识别驱动 UI 操作**：所有交互基于 Airtest 模板匹配（点击图片、等待图片、断言图片存在），不依赖控件 ID
- **多级 fallback 设备连接**：[connect.py](modules/common/connect.py) 先试 adb devices 列表、再扫常见模拟器端口（夜神/雷电/BlueStacks/MuMu/MEmu/AVD/WSA）
- **登录优先策略**：登录失败立即终止整轮测试，避免后续依赖登录态的用例无意义失败
- **自研报告系统**：相比原生 Allure，提供了中文 Dashboard、Top10 失败用例统计、趋势图，并内置 30 天历史归档
- **OCR 数值校验**：集成 RapidOCR 单例 + 单位换算（K/M/B），可校验游戏内金币等数值；模块加载时**懒初始化**，未安装只抛 ImportError 不阻断项目启动

## 常用命令

### 安装依赖
```bash
# Python 核心依赖（必装）
pip install -r requirements.txt

# OCR 依赖（可选，仅做金币数值校验时需要）
pip install rapidocr-onnxruntime

# Node.js 依赖（报告服务）
cd report
npm install
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
```bash
# 方式一：通过 main.py 启动（推荐，自动管理生命周期）
python main.py
# 服务会随 pytest 一起启动，跑完后保持运行

# 方式二：手动启动（独立运行）
cd report
node server.js

# 方式三：通过 report_server.py（带启动检测 + 日志）
python report_server.py            # 启动
python report_server.py --stop     # 停止

# 访问：
# - 聚合报告 Dashboard: http://127.0.0.1:8090
# - 单次详细报告: http://127.0.0.1:8090/detail.html?name=<时间戳>
```

### 工具脚本
```bash
# 清理 30 天前的旧报告（自动在 main.py 末尾调用）
python clean.py

# 批量重新生成历史报告
python report/refreshGenerate.py

# 报告服务管理（端口检测 + 日志 + 旧进程清理）
python report_server.py            # 启动
python report_server.py --stop     # 停止残留服务
```

## 项目架构

### 目录结构
```
├── main.py                          # 主入口，编排整个测试流程
├── report_server.py                 # 报告服务管理（启动检测 + 端口等待 + 旧进程清理）
├── conf.py                          # 静态配置管理（get_package / make_example_name / EXAMPLE_NAME_ENV）
├── clean.py                         # 归档 30 天前的旧报告
├── conftest.py                      # pytest 全局 fixture（自动连接设备、自动截图）
├── config.json                      # 配置文件（仅含 package 字段）
├── order.yaml                       # 用例执行顺序配置
├── requirements.txt                 # Python 依赖清单（含可选 OCR）
├── pytest.ini                       # pytest 配置（filterwarnings、markers）
│
├── modules/
│   ├── common/                      # 公共封装层（Airtest API 二次封装）
│   │   ├── connect.py               # 多级 fallback 设备连接（adb devices → 常见模拟器端口）
│   │   ├── functionAPI.py           # 图片点击/等待/查找/区域截图
│   │   ├── sceenShot.py             # 自动截图到报告目录
│   │   ├── startApp.py              # 通过 package 字段重启 App
│   │   ├── imgDict.py               # 扫描 img/ 目录成字典
│   │   ├── checkData.py             # OCR + 单位换算（K/M/B）
│   │   ├── getFunctionName.py       # 反射获取调用方名
│   │   ├── base_test.py             # 测试基类（自动加载 img/）
│   │   ├── close/closeAllWindows.py # 循环点击关闭弹窗
│   │   └── ocr/rapidOCR.py          # RapidOCR 多版本输出兼容
│   │
│   ├── function/                    # 业务用例层
│   │   ├── conftest.py              # 提供 img_dict fixture
│   │   └── login/                   # 登录模块
│   │       ├── test_login.py        # 登录全流程用例
│   │       └── img/                 # UI 识别图片
│   │
│   └── sample.py                    # 用例模板
│
└── report/                          # 自研 Web 报告系统
    ├── server.js                    # Express 服务（端口 8090；BlueStack 占 8080 故避开）
    ├── index.html                   # 聚合报告 Dashboard
    ├── report.js                    # Dashboard 逻辑（Chart.js 图表、表格）
    ├── detail.html                  # 单次详细报告
    ├── generateReport.js            # 单次报告生成器
    ├── process.js                   # summary.json 统计逻辑
    ├── summary.js                   # 扫描 allure-results 生成 summary
    ├── refreshGenerate.py           # 批量重新生成历史报告
    └── public/                      # 静态资源（背景图等）
```

### 核心数据流

**一次 `python main.py` 的完整链路**：

1. **启动报告服务**：Node 起的 Express 在 8090 提供历史报告查询（端口被 BlueStack 占时由 [report_server.py](report_server.py) 检测并提示）
2. **时间戳初始化**：[main.py](main.py) 调 `make_example_name()` 生成 14 位时间戳，写入环境变量 `EXAMPLE_NAME` 让子进程可见（**不再写入 config.json**）
3. **连接设备**：`conftest.py` session 级 fixture 调 [androidConnect()](modules/common/connect.py)，走 adb devices → 常见模拟器端口的多级 fallback
4. **跑登录**：`pytest -x` 跑 `test_login.py`，登录失败直接终止整轮
5. **跑其它用例**：登录成功后按 `order.yaml` 顺序跑其它模块（`--maxfail=3` 容忍 3 个失败）
6. **自动截图**：每个用例执行前后由 fixture 自动截屏，命名 `类名_方法名.jpg`（[sceenShot.py](modules/common/sceenShot.py) 从环境变量读 `EXAMPLE_NAME`）
7. **Allure HTML**：`allure generate` 产出 `html/` 报告
8. **报告清理**：`clean.py` 把 30 天前报告归档到 `history/`
9. **生成单次报告**：`generateReport.js` 写出本轮报告目录
10. **刷新聚合数据**：`summary.js` + `process.js` 重建 `summary/`

### 报告目录结构
```
report/
├── allure-results/
│   └── <14位时间戳>/
│       ├── json/                    # allure 原始 JSON
│       ├── html/                    # allure HTML 报告
│       ├── img/                     # 测试截图（类名_方法名.jpg）
│       └── log/execution.log        # 执行日志
├── summary/
│   └── <14位时间戳>.json            # 聚合统计（sum、passed、failExample）
└── history/                         # 30 天前归档目录（[clean.py](clean.py) 自动迁移）
```

## 关键设计约束

### 1. 用例命名规范
- **类名必须全局唯一**：截图按 `类名_方法名.jpg` 命名，类名重复会导致截图覆盖
- **测试方法以 `test_` 开头**：遵循 pytest 规范
- **用例类内部顺序**：通过 `@pytest.mark.order` 控制
- **模块和类的执行顺序**：通过 `order.yaml` 配置

### 2. 图像识别机制
- 所有 UI 操作基于图片模板匹配，不依赖 Android 控件 ID
- 图片资源放在 `modules/function/<module>/img/` 目录
- 使用 `imgDict` 字典访问图片，key 为文件名（不含扩展名）

### 3. 登录优先策略
- `main.py` 第一阶段单独跑登录，`pytest -x` 失败立即终止
- 避免后续依赖登录态的用例在未登录态空跑
- 登录通过后才读取 `order.yaml` 跑其它模块

### 4. 多级 fallback 设备连接
- [connect.py](modules/common/connect.py) 的 `androidConnect()` 采用 **adb devices 列表 → 常见模拟器端口** 的两级 fallback
- 模拟器端口清单在 `COMMON_EMULATOR_PORTS` 常量里（11 个：夜神/雷电/BlueStacks/MuMu/MEmu/AVD/WSA）
- URI 模板集中在 `DEVICE_URI_SUFFIX = "?cap_method=javacap&touch_method=adb"`，改截图/触屏方式只动一处
- 全部失败时 RuntimeError 会列出已尝试内容 + 4 条排查建议（**不要静默 fallback 到一个错的设备**）

### 5. 报告系统自研
- 完全自研的 Web 报告，不使用原生 Allure UI
- 聚合报告 Dashboard：总运行次数/通过/失败/通过率、Top10 失败用例柱状图、通过率趋势折线图
- 单次详细报告：四宫格汇总 + 进度条 + 全部/通过/失败筛选 + 分页 + 截图/错误信息弹窗（[detail.html](report/detail.html) 用 `display:block` + ellipsis 防止错误信息撑破列宽）
- 内置 30 天历史归档机制（[clean.py](clean.py) 可调阈值）

## 编写新用例

### 新增模块
在 `modules/function/` 下创建新目录：
```
modules/function/new_module/
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
from modules.common.functionAPI import *
from modules.common.sceenShot import *
from modules.common.imgDict import *

class TestExample:  # 类名必须全局唯一

    @allure.step("执行测试步骤")
    def test_example(self):
        """测试用例示例"""
        # 截图（自动保存到报告目录）
        auto_screenshot("步骤描述")

        # 点击图片
        click_img("button.png", "点击失败")

        # 等待图片出现
        wait_img("loading.png")

        # 检查图片是否存在
        exists_img("success.png", "未找到成功页面")
```

### 添加到执行顺序
在 `order.yaml` 中添加：
```yaml
- modules.function.new_module.test_newmodule.TestExample
```

## 常见任务

### 调试单个用例
```bash
# 启用详细输出
pytest -s -v modules/function/login/test_login.py::TestLogin::test_login

# 只跑特定标记的用例
pytest -s -m order modules/function/login/

# 失败时进入调试
pytest -s --pdb modules/function/login/test_login.py
```

### 手动触发报告清理
```bash
python clean.py
```

### 批量重新生成历史报告
```bash
python report/refreshGenerate.py
```

### 修改报告端口
编辑 `report/server.js` 中的 `port` 变量（**同时需同步更新 [report/report.js](report/report.js) 和 [report/detail.html](report/detail.html) 中的 `API_BASE` 与 `getServerIP`**）。

## 依赖说明

### Python 核心依赖
完整版本见 [requirements.txt](requirements.txt)（含版本下限约束和分组注释）。要点：

- `airtest`：UI 自动化框架
- `pytest`：测试运行器
- `opencv-python`：图像处理（airtest 内部强依赖）
- `allure-pytest`：Allure 报告集成（**注意：allure 命令行工具要单独装**，brew/scoop/npm 任选）
- `pyyaml`：YAML 配置解析

可选：
- `rapidocr-onnxruntime`：OCR 数值校验（金币等），**模块懒加载**，未装时只抛 ImportError 不阻断项目启动

### Node.js 依赖
- `express`：Web 服务器
- `chart.js`：图表库（通过 CDN 引入）
- `parcel`：打包工具（package.json 里，当前未使用，可清理）

## 后续优化方向

- 性能优化：并发跑多设备
- 报告增强：接入更多图表（用例执行时长分布、模块通过率对比）
- 用例管理：支持用例标签、跳过、参数化
- 图像识别：集成深度学习模型提升识别准确率
- CI/CD 集成：Jenkins/GitHub Actions 自动化触发
- 异常处理：网络断开、App 崩溃、ANR 等场景的自动恢复
