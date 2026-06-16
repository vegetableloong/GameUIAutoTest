"""
报告服务管理模块：封装 Node Express 服务的启动、停止与就绪检测。

解决的问题：
1. Popen 静默失败（端口被占、Node 报错都不知道）
2. 启动后没等就绪就继续往下走
3. 多次运行累积僵尸 node 进程
4. Node 输出和 Python 输出混在一起，难以排查
"""
import os
import sys
import time
import socket
import signal
import platform
import subprocess
from pathlib import Path
from typing import Optional


# 默认端口，与 report/server.js 中保持一致
DEFAULT_PORT = 8090
# 启动超时：服务最多等待 N 秒仍未监听则报错
STARTUP_TIMEOUT = 10
# 端口探测间隔
POLL_INTERVAL = 0.2


def _is_port_listening(port: int, host: str = "127.0.0.1") -> bool:
    """检查指定端口是否处于 LISTEN 状态"""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False


def _kill_existing_server() -> None:
    """
    杀掉残留的 node server.js 进程，避免端口冲突。
    Unix 系统用 pkill，Windows 用 taskkill（best-effort，失败不抛错）。
    """
    if platform.system() == "Windows":
        cmd = ["taskkill", "/F", "/FI", "IMAGENAME eq node.exe", "/FI", "WINDOWTITLE eq *server.js*"]
    else:
        # -f 匹配完整命令行，确保只杀 server.js 不误伤其它 node 进程
        cmd = ["pkill", "-f", "node.*report/server.js"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("🧹  已清理残留的报告服务进程")
            # 等待 OS 释放端口
            time.sleep(0.5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # 工具不可用就静默跳过（不强依赖）
        pass
    except Exception as e:
        # 任何其它异常也不影响主流程
        print(f"⚠️  清理旧进程时遇到非致命错误: {e}")


def _wait_for_port(port: int, timeout: float) -> float:
    """
    等待端口开始监听，返回实际等待秒数。
    超时返回 -1。
    """
    start = time.time()
    while time.time() - start < timeout:
        if _is_port_listening(port):
            return time.time() - start
        time.sleep(POLL_INTERVAL)
    return -1


def start_server(
    log_dir: Optional[str] = None,
    port: int = DEFAULT_PORT,
    timeout: float = STARTUP_TIMEOUT,
) -> subprocess.Popen:
    """
    启动报告服务，等待端口就绪后返回进程对象。

    :param log_dir: 日志目录；None 时输出到 DEVNULL。传入则同时输出到日志文件和 stdout。
    :param port: 期望监听的端口
    :param timeout: 启动超时秒数
    :return: 启动成功的 Popen 对象
    :raises RuntimeError: 启动失败或超时
    """
    # 1. 清理旧进程（避免端口冲突 + 僵尸进程累积）
    _kill_existing_server()

    # 2. 准备日志
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "report-server.log")
        # 追加模式，保留历次启动日志
        log_file = open(log_path, "a", encoding="utf-8")
        # 同时输出到 stdout 和日志文件，方便实时观察
        process = subprocess.Popen(
            ["node", "./report/server.js"],
            stdout=subprocess.PIPE,  # 单独管道，下面用线程转发
            stderr=subprocess.STDOUT,
        )
        _start_log_forwarder(process, log_file)
        print(f"📝  报告服务日志: {log_path}")
    else:
        process = subprocess.Popen(
            ["node", "./report/server.js"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    # 3. 等待端口就绪
    elapsed = _wait_for_port(port, timeout)
    if elapsed < 0:
        # 超时：杀掉刚启动的进程，给出可操作的错误提示
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
        raise RuntimeError(
            f"报告服务启动超时（{timeout}秒），端口 {port} 未监听。\n"
            f"可能原因：\n"
            f"  1. 端口被其他程序占用：运行 `lsof -i :{port}` 排查\n"
            f"  2. Node 启动失败：查看上方日志或日志文件\n"
            f"  3. 缺少依赖：运行 `cd report && npm install`"
        )

    print(f"✅  报告服务已就绪 (PID {process.pid}, 用时 {elapsed:.1f}s)")
    print(f"    访问: http://127.0.0.1:{port}/")
    return process


def _start_log_forwarder(process: subprocess.Popen, log_file) -> None:
    """
    启动后台线程把子进程的 stdout 实时转发到日志文件 + 主进程 stdout。
    避免 Popen 输出被缓冲，导致启动失败时看不到错误。
    """
    import threading

    def _forward():
        try:
            for line in iter(process.stdout.readline, b""):
                decoded = line.decode("utf-8", errors="replace")
                log_file.write(decoded)
                log_file.flush()
                sys.stdout.write(decoded)
                sys.stdout.flush()
        except Exception:
            pass
        finally:
            log_file.close()

    thread = threading.Thread(target=_forward, daemon=True)
    thread.start()


def stop_server(process: Optional[subprocess.Popen], timeout: float = 5) -> None:
    """
    优雅停止报告服务。先 SIGTERM，等不到再 SIGKILL。
    传入 None 时静默跳过。
    """
    if process is None:
        return
    if process.poll() is not None:
        # 已经退出了
        return

    try:
        process.terminate()
        process.wait(timeout=timeout)
        print("✅  报告服务已停止")
    except subprocess.TimeoutExpired:
        process.kill()
        print("⚠️  报告服务被强制终止")
    except Exception as e:
        print(f"⚠️  停止报告服务时出错: {e}")


# 命令行入口：方便手动测试
if __name__ == "__main__":
    """
    用法：
        python report_server.py            # 启动服务（Ctrl+C 停止）
        python report_server.py --stop     # 停止已有服务
    """
    if "--stop" in sys.argv:
        _kill_existing_server()
        print("已停止")
    else:
        proc = start_server()
        try:
            # 阻塞直到用户 Ctrl+C
            proc.wait()
        except KeyboardInterrupt:
            stop_server(proc)
