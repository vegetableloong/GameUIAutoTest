from datetime import datetime
import json
import os

def save_exampleName():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "config.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["exampleName"] = timestamp

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 已写入 config.json：{timestamp}")
    return timestamp

def load_exampleName():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "config.json")

    if not os.path.exists(json_path):
        print("⚠️ 未找到 config.json")
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("exampleName")
