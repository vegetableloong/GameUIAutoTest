# UI自动化测试

基于 Airtest + Pytest 二次封装的 UI 自动化测试工具，支持 Android 应用自动化测试。

## 功能特性

- **UI 自动化测试**：基于 Airtest 框架，支持图片识别和坐标操作
- **测试报告系统**：现代化的 Web 报告界面，支持聚合报告和详细报告
- **失败用例统计**：自动统计高频失败用例，帮助快速定位问题
- **报告过期清理**：自动清理 365 天前的旧报告

## 快速开始

### 环境要求

- Python 3.9+
- Node.js (用于报告服务器)

### 安装依赖

```bash
# Python 依赖
pip install airtest pytest

# Node.js 依赖
cd report
npm install
```

### 运行测试

```bash
python main.py
```

### 查看报告

```bash
cd report
node server.js
```

访问 http://127.0.0.1/:8080 查看测试报告。

## 目录结构

```
|-- /
    |-- modules/
    |   |-- common/                    # 公共模块，封装了通用接口
    |   |   |-- connect.py             # 设备连接
    |   |   |-- functionAPI.py         # 封装 Airtest API
    |   |   |-- getFunctionName.py     # 获取函数名
    |   |   |-- imgDict.py             # 图片字典管理
    |   |   |-- sceenShot.py           # 截图
    |   |   |-- startApp.py            # 启动应用
    |   |   |-- checkData.py           # 数据校验（OCR等）
    |   |-- function/                  # 功能模块，测试用例编写目录
    |       |-- login/                 # 登录测试模块
    |       |   |-- test_login.py      # 测试用例（pytest 规范：test_ 开头）
    |       |   |-- img/               # UI 识别图片
    |       |   |   |-- main_view.png
    |-- report/                        # 测试报告目录
    |   |-- index.html                 # 聚合报告首页
    |   |-- detail.html                # 详细测试报告
    |   |-- report.js                  # 聚合报告逻辑
    |   |-- server.js                  # 报告服务器
    |   |-- summary/                   # 聚合报告数据
    |   |-- allure-results/            # 单次测试结果目录
    |   |-- history/                   # 历史报告（365天前自动移动到此）
    |-- clean.py                       # 报告清理脚本
    |-- conftest.py                    # pytest 配置
    |-- main.py                        # 主入口
    |-- config.json                    # 配置文件
    |-- order.yaml                     # 用例执行顺序配置
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
  "exampleName": "20260116151330"
}
```

### order.yaml

控制用例执行顺序：

```yaml
- modules.function.login.test_login.TestLogin
```
