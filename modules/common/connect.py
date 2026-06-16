from airtest.core.api import *
import subprocess
from typing import List, Optional, Tuple

# 常见 Android 模拟器/沙箱的 ADB 端口
# 来源：各模拟器官方文档 + 实际测试经验
#   5555        - 雷电、BlueStacks 5、Genymotion、AVD、腾讯手游、小米
#   5554/5556/5557 - 雷电/AVD 副端口
#   62001/62025/62026 - 夜神 (Nox)
#   7555/7556   - 网易 MuMu
#   21503       - 逍遥 (MEmu)
#   58526       - WSA (Windows Subsystem for Android)
COMMON_EMULATOR_PORTS: List[Tuple[str, int]] = [
    ("127.0.0.1", 5555),
    ("127.0.0.1", 5554),
    ("127.0.0.1", 5556),
    ("127.0.0.1", 5557),
    ("127.0.0.1", 62001),
    ("127.0.0.1", 62025),
    ("127.0.0.1", 62026),
    ("127.0.0.1", 7555),
    ("127.0.0.1", 7556),
    ("127.0.0.1", 21503),
    ("127.0.0.1", 58526),
]

# Airtest 设备 URI 中固定的两项截图/触屏方法参数
#   cap_method=javacap   - 兼容性最好的截图方式（几乎所有模拟器/真机都支持）
#   touch_method=adb     - 用 adb shell input 模拟触屏，比 minicap 稳定
DEVICE_URI_SUFFIX = "?cap_method=javacap&touch_method=adb"


def get_adb_devices() -> List[str]:
    """获取 adb devices 列表（仅返回 state == 'device' 的）"""
    try:
        result = subprocess.run(
            ['adb', 'devices'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        print("❌ 未找到 adb 命令，请先安装 Android Platform Tools")
        return []
    except Exception as e:
        print(f"❌ adb 命令执行失败: {e}")
        return []

    devices: List[str] = []
    for line in result.stdout.strip().split('\n')[1:]:
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) == 2 and parts[1].strip() == 'device':
            devices.append(parts[0])
    return devices


def _adb_connect(host: str, port: int) -> bool:
    """adb connect host:port 一次，成功（或已连接）返回 True"""
    try:
        result = subprocess.run(
            ['adb', 'connect', f'{host}:{port}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        output = (result.stdout + result.stderr).lower()
        return 'connected' in output  # 覆盖 "connected to" 和 "already connected"
    except Exception:
        return False


def _try_airtest_connect(uri: str) -> Optional[object]:
    """调用 airtest.connect_device 一次，失败返回 None（捕获所有异常）"""
    try:
        return connect_device(uri)
    except Exception as e:
        print(f"    失败: {type(e).__name__}: {e}")
        return None


def androidConnect():
    """
    多级 fallback 连接 Android 设备。

    策略：
      1. 先遍历 adb devices 列表中的设备（按顺序逐个尝试）
      2. 全部失败后，扫描常见模拟器端口：先 adb connect，再用 airtest 连接
      3. 仍然失败时抛出带排查建议的 RuntimeError
    """
    # ===== 第 1 级：adb devices 列表 =====
    devices = get_adb_devices()
    print(f"📱 adb devices 列表: {devices or '空'}")

    if devices:
        print("尝试 adb devices 列表中的设备...")
        for i, device in enumerate(devices, 1):
            print(f"  [{i}/{len(devices)}] {device}")
            uri = f"Android:///{device}{DEVICE_URI_SUFFIX}"
            conn = _try_airtest_connect(uri)
            if conn is not None:
                print(f"✅ {device} 设备已连接")
                sleep(2)
                return conn
        print("⚠️  列表中的设备均连接失败")

    # ===== 第 2 级：常见模拟器端口 =====
    print("\n尝试常见模拟器端口（夜神/雷电/BlueStacks/MuMu/MEmu/AVD/WSA）...")
    for host, port in COMMON_EMULATOR_PORTS:
        addr = f"{host}:{port}"
        print(f"  尝试 {addr}...")
        if not _adb_connect(host, port):
            print(f"    adb connect 失败")
            continue
        uri = f"Android:///{addr}{DEVICE_URI_SUFFIX}"
        conn = _try_airtest_connect(uri)
        if conn is not None:
            print(f"✅ 模拟器已连接: {addr}")
            sleep(2)
            return conn

    # ===== 全部失败 =====
    raise RuntimeError(
        "\n❌ 无法连接任何 Android 设备。\n"
        "已尝试：\n"
        f"  1. adb devices 列表（{len(devices)} 个设备）\n"
        f"  2. {len(COMMON_EMULATOR_PORTS)} 个常见模拟器端口\n"
        "\n排查建议：\n"
        "  - 模拟器是否已启动？\n"
        "  - 真机：USB 调试是否打开？数据线是否正常？\n"
        "  - adb 服务是否正常：adb kill-server && adb start-server\n"
        "  - 是否需要特殊端口（非 127.0.0.1）？可手动 adb connect 后重试"
    )


# Windows 连接（保留原样，未做改动）
def windowsConnect(**handle):
    if handle is exists:
        conn = connect_device("Windows:///" + handle)
    else:
        conn = connect_device("Windows:///")
    print("Windows已连接")
    sleep(2)
    return conn
