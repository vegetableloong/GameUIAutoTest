"""
批量重新生成历史报告：对 allure-results 下每个时间戳目录都跑一次 generateReport.js。

用法：
    python report/refreshGenerate.py
"""
import os
import subprocess
import sys

# 项目根目录（此文件位于 report/ 子目录，向上 1 级）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLURE_RESULTS = os.path.join(BASE_DIR, "report", "allure-results")
GENERATE_SCRIPT = os.path.join(BASE_DIR, "report", "generateReport.js")


def list_run_folders(base: str) -> list:
    """列出 allure-results 下所有 14 位时间戳子目录"""
    if not os.path.isdir(base):
        print(f"⚠️  目录不存在: {base}")
        return []
    return sorted(
        entry.name
        for entry in os.scandir(base)
        if entry.is_dir() and entry.name.isdigit() and len(entry.name) == 14
    )


def regenerate(folder_name: str) -> bool:
    """对单个目录重新生成报告，返回是否成功"""
    try:
        subprocess.run(
            ["node", GENERATE_SCRIPT, folder_name],
            check=True,
            cwd=BASE_DIR,
            timeout=60
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {folder_name} 失败: {e}")
        return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {folder_name} 超时（60s）")
        return False


def main() -> int:
    folders = list_run_folders(ALLURE_RESULTS)
    if not folders:
        print("没有可刷新的报告目录")
        return 0

    print(f"找到 {len(folders)} 个报告目录，开始刷新...\n")
    success = 0
    for name in folders:
        print(f"🔄 刷新 {name} ... ", end="", flush=True)
        if regenerate(name):
            print("✅")
            success += 1

    print(f"\n完成：{success}/{len(folders)} 成功")
    return 0 if success == len(folders) else 1


if __name__ == "__main__":
    sys.exit(main())
