#!/usr/bin/env python3
"""
Wind Windows 常驻服务 - 使用命名管道实现单实例连接共享

解决 Windows 下 Wind 单实例限制问题：
- 避免每次脚本都需登录
- 避免抢占桌面 Wind 终端
- 多个客户端可复用同一连接

启动: python wind_server_win.py
停止: Ctrl+C 或发送 {"cmd": "shutdown"}
"""

import json
import os
import pickle
import struct
import sys
import threading
import time
import traceback

# Windows 使用命名管道
import win32pipe
import win32file
import pywintypes

# 添加 WindPy 路径
try:
    from WindPy import w
except ImportError:
    print("错误: 未找到 WindPy，请确保 Wind 终端已安装")
    sys.exit(1)

# 管道名称
PIPE_NAME = r'\\.\pipe\WindPyServer'

# 全局锁和数据
_lock = threading.Lock()
_results = {}
_request_id = 0


def _ensure_connected():
    """确保 Wind 已连接"""
    if not w.isconnected():
        print("[WindWinServer] 正在连接 Wind...")
        ret = w.start()
        if not w.isconnected():
            raise RuntimeError(f"Wind 连接失败: {ret}")
        print("[WindWinServer] Wind 连接成功")
    return w


def _execute_wind_api(func_name, args, kwargs):
    """执行 Wind API 调用"""
    try:
        w = _ensure_connected()
        func = getattr(w, func_name)
        result = func(*args, **kwargs)
        return {"success": True, "error_code": result.ErrorCode, "data": result.Data}
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def handle_client(pipe_handle):
    """处理客户端请求"""
    try:
        # 读取请求长度
        size_data = win32file.ReadFile(pipe_handle, 4)
        size = struct.unpack('I', size_data[1])[0]

        # 读取请求数据
        data = b''
        while len(data) < size:
            chunk = win32file.ReadFile(pipe_handle, min(4096, size - len(data)))
            data += chunk[1]

        request = pickle.loads(data)
        func_name = request.get('func')
        args = request.get('args', [])
        kwargs = request.get('kwargs', {})

        print(f"[WindWinServer] 执行: {func_name}({', '.join(map(str, args))})")

        # 执行 Wind API
        result = _execute_wind_api(func_name, args, kwargs)

        # 发送响应
        response_data = pickle.dumps(result)
        response_size = struct.pack('I', len(response_data))
        win32file.WriteFile(pipe_handle, response_size)
        win32file.WriteFile(pipe_handle, response_data)

    except Exception as e:
        print(f"[WindWinServer] 处理请求错误: {e}")
    finally:
        win32file.CloseHandle(pipe_handle)


def server_loop():
    """服务器主循环"""
    print(f"[WindWinServer] 正在启动...")
    print(f"[WindWinServer] 管道: {PIPE_NAME}")

    # 首先连接 Wind
    try:
        _ensure_connected()
    except Exception as e:
        print(f"[WindWinServer] Wind 连接失败: {e}")
        return

    print(f"[WindWinServer] 服务已启动，等待客户端连接...")
    print(f"[WindWinServer] 提示: 在另一个终端运行客户端脚本")

    while True:
        try:
            # 创建命名管道
            pipe_handle = win32pipe.CreateNamedPipe(
                PIPE_NAME,
                win32pipe.PIPE_ACCESS_DUPLEX,
                win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                win32pipe.PIPE_UNLIMITED_INSTANCES,
                65536, 65536, 0, None
            )

            # 等待客户端连接
            win32pipe.ConnectNamedPipe(pipe_handle, None)

            # 处理请求
            handle_client(pipe_handle)

        except KeyboardInterrupt:
            print("\n[WindWinServer] 收到中断信号，正在关闭...")
            break
        except Exception as e:
            print(f"[WindWinServer] 错误: {e}")
            time.sleep(1)

    # 清理
    if w.isconnected():
        w.stop()
    print("[WindWinServer] 已停止")


if __name__ == "__main__":
    try:
        server_loop()
    except KeyboardInterrupt:
        print("\n[WindWinServer] 已退出")
