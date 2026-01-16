import os
import time
import shutil
import datetime

# 设置路径
base_dir = os.path.dirname(os.path.abspath(__file__))
allure_path = os.path.join(base_dir, "report", "allure-results")
summary_path = os.path.join(base_dir, "report", "summary")
backup_path = os.path.join(base_dir, "report", "history")

# 清理的时间阈值（天）
days_threshold = 365
now = datetime.datetime.now()
cutoff = now - datetime.timedelta(days=days_threshold)
print(cutoff)

# 判断目录名是否为有效时间格式
def parse_datetime_from_name(name):
    base_name = os.path.splitext(name)[0]
    try:
        return datetime.datetime.strptime(base_name, "%Y%m%d%H%M%S")
    except ValueError:
        return None

# 移动过期报告
def moveReport(target_path):
    print(f"进入清理流程: {target_path}")
    for item in os.listdir(target_path):
        item_path = os.path.join(target_path, item)

        # 跳过隐藏文件
        if item.startswith("."):
            continue

        item_time = parse_datetime_from_name(item)
        if item_time is None:
            print(f"跳过无效时间格式文件/目录: {item}")
            continue

        if item_time < cutoff:
            dest_path = os.path.join(backup_path, item)
            if os.path.exists(dest_path):
                print(f"目标已存在，跳过: {dest_path}")
                continue

            print(f"正在移动: {item_path} -> {dest_path}")
            try:
                shutil.move(item_path, dest_path)
            except Exception as e:
                print(f"移动失败: {item_path}, 错误: {e}")

def backup():
    os.makedirs(backup_path, exist_ok=True)
    moveReport(allure_path)
    moveReport(summary_path)
