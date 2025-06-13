from airtest.core.api import *
import subprocess

#adb获取devices列表
def get_adb_devices():
    try:
        result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout
        lines = output.strip().split('\n')

        devices = []
        for line in lines[1:]:  # Skip the first line: "List of devices attached"
            if line.strip():
                parts = line.split('\t')
                if len(parts) == 2 and parts[1] == 'device':
                    devices.append(parts[0])

        return devices
    except Exception as e:
        print(f"Error: {e}")
        return []


#Android连接
def androidConnect():
    devices = get_adb_devices()
    print("设备列表：", devices)
    conn = connect_device("Android:///" + devices[0] + "?cap_method=javacap&touch_method=adb")
    print(devices[0] + "设备已连接")
    sleep(2)
    return conn

#Windows连接
def windowsConnect(**handle):
    if handle is exists:
        conn = connect_device("Windows:///" + handle)
    else:
        conn = connect_device("Windows:///")
    print("Windows已连接")
    sleep(2)
    return conn