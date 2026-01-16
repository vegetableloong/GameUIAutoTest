import os
import subprocess

base_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(base_dir, 'allure-results')
folders = [entry.name for entry in os.scandir(folder_path) if entry.is_dir()]

print(folders)

for exampleName in folders:
    # 生成单独报告
    subprocess.run(["node", "./generateReport.js", exampleName])
    print("✅ 刷新", exampleName)