#!/usr/bin/env python3
"""
Wind 常驻服务 — 保持 WindPy 长连接，通过本地 HTTP 接口提供数据查询。

启动: python wind_server.py [--host 127.0.0.1] [--port 18888] [--pidfile <path>]
停止: curl http://localhost:18888/shutdown  或  kill $(cat <pidfile>)

环境变量 (优先级低于命令行参数):
  WIND_SERVER_HOST    — 绑定地址 (默认 127.0.0.1)
  WIND_SERVER_PORT    — 端口 (默认 18888)
  WIND_SERVER_PIDFILE — PID 文件路径 (默认 系统临时目录/wind_server.pid)

支持的接口:
  POST /wsd    — w.wsd()    日级时间序列
  POST /wss    — w.wss()    截面快照
  POST /wset   — w.wset()   报表数据集
  POST /wsq    — w.wsq()    实时行情快照
  POST /edb    — w.edb()    宏观经济指标
  POST /wsi    — w.wsi()    分钟K线序列
  POST /wst    — w.wst()    日内Tick跳价
  POST /wsee   — w.wsee()   板块多维数据
  POST /wses   — w.wses()   板块时间序列
  POST /wsed   — w.wsed()   板块查询
  POST /tdays  — w.tdays()  交易日列表
  POST /tdaysoffset — w.tdaysoffset()  交易日偏移
  POST /tdayscount  — w.tdayscount()   交易日计数
  POST /weqs   — w.weqs()   条件选股
  POST /htocode — w.htocode() 代码转换
  POST /wai    — w.wai()    智能API
  POST /wgel   — w.wgel()   企业库
  GET  /health — 健康检查
  GET  /shutdown — 优雅关闭
"""

import argparse
import json
import os
import signal
import sys
import tempfile
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# ---------------------------------------------------------------------------
# Wind 连接管理
# ---------------------------------------------------------------------------
_wind_lock = threading.Lock()
_w = None


def _ensure_connected():
    """确保 Wind 已连接，断线自动重连。"""
    global _w
    with _wind_lock:
        if _w is None:
            from WindPy import w as _wind
            _w = _wind
        if not _w.isconnected():
            ret = _w.start(waitTime=30)
            if not _w.isconnected():
                raise RuntimeError(f"Wind connect failed: {ret}")
    return _w


def _wind_data_to_dict(result):
    """将 WindData 对象转成可序列化的 dict。"""
    if hasattr(result, 'ErrorCode') and result.ErrorCode != 0:
        return {"error": True, "code": result.ErrorCode, "message": str(getattr(result, 'Data', ''))}

    out = {
        "ErrorCode": result.ErrorCode,
        "Codes": result.Codes if hasattr(result, 'Codes') else [],
        "Fields": result.Fields if hasattr(result, 'Fields') else [],
        "Times": [str(t) for t in result.Times] if hasattr(result, 'Times') and result.Times else [],
    }
    # Data: list of lists, 需要处理日期等不可序列化类型
    if hasattr(result, 'Data') and result.Data:
        data = []
        for row in result.Data:
            data.append([_serialize(v) for v in row])
        out["Data"] = data
    else:
        out["Data"] = []
    return out


def _serialize(v):
    """将单个值转为 JSON 可序列化类型。"""
    if v is None:
        return None
    if isinstance(v, (int, float, str, bool)):
        return v
    return str(v)


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------
class WindHandler(BaseHTTPRequestHandler):
    """处理 Wind 查询请求。"""

    def log_message(self, fmt, *args):
        # 静默日志，避免刷屏
        pass

    def _json_response(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    # --- GET ---
    def do_GET(self):
        if self.path == "/health":
            try:
                w = _ensure_connected()
                self._json_response({"status": "ok", "connected": w.isconnected()})
            except Exception as e:
                self._json_response({"status": "error", "message": str(e)}, 503)

        elif self.path == "/shutdown":
            self._json_response({"status": "shutting down"})
            threading.Thread(target=self.server.shutdown, daemon=True).start()

        else:
            self._json_response({"error": "not found"}, 404)

    # --- POST ---
    def do_POST(self):
        try:
            params = self._read_body()
            w = _ensure_connected()

            if self.path == "/wsd":
                result = w.wsd(
                    params["codes"], params["fields"],
                    params.get("beginTime", ""), params.get("endTime", ""),
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/wss":
                result = w.wss(
                    params["codes"], params["fields"],
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/wset":
                result = w.wset(
                    params["tableName"],
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/wsq":
                result = w.wsq(
                    params["codes"], params["fields"],
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/edb":
                result = w.edb(
                    params["codes"],
                    params.get("beginTime", ""), params.get("endTime", ""),
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/wsi":
                result = w.wsi(
                    params["codes"], params["fields"],
                    params.get("beginTime", ""), params.get("endTime", ""),
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/wst":
                result = w.wst(
                    params["codes"], params["fields"],
                    params.get("beginTime", ""), params.get("endTime", ""),
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/wsee":
                result = w.wsee(
                    params["codes"], params["fields"],
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/wses":
                result = w.wses(
                    params["codes"], params["fields"],
                    params.get("beginTime", ""), params.get("endTime", ""),
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/wsed":
                result = w.wsed(
                    params["codes"], params["fields"],
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/tdays":
                result = w.tdays(
                    params.get("beginTime", ""), params.get("endTime", ""),
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/tdaysoffset":
                result = w.tdaysoffset(
                    params["offset"],
                    params.get("beginTime", ""),
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/tdayscount":
                result = w.tdayscount(
                    params.get("beginTime", ""), params.get("endTime", ""),
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/weqs":
                result = w.weqs(
                    params["filtername"],
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/htocode":
                result = w.htocode(
                    params["codes"], params["sec_type"],
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/wai":
                result = w.wai(
                    params["func"], params["input"],
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            elif self.path == "/wgel":
                result = w.wgel(
                    params["funname"], params["windid"],
                    params.get("options", ""),
                )
                self._json_response(_wind_data_to_dict(result))

            else:
                self._json_response({"error": "unknown endpoint"}, 404)

        except Exception as e:
            self._json_response({"error": True, "message": str(e)}, 500)


# ---------------------------------------------------------------------------
# 启动入口
# ---------------------------------------------------------------------------
def main():
    default_port = int(os.environ.get("WIND_SERVER_PORT", 18888))
    default_host = os.environ.get("WIND_SERVER_HOST", "127.0.0.1")
    default_pid = os.environ.get(
        "WIND_SERVER_PIDFILE",
        os.path.join(tempfile.gettempdir(), "wind_server.pid"),
    )

    parser = argparse.ArgumentParser(description="Wind 常驻服务")
    parser.add_argument("--port", type=int, default=default_port)
    parser.add_argument("--host", type=str, default=default_host)
    parser.add_argument("--pidfile", type=str, default=default_pid)
    args = parser.parse_args()

    pid_file = args.pidfile

    # 写 PID 文件
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    # macOS: 检测 WindPy 环境，自动修复 symlink
    try:
        from setup_windpy import ensure_windpy
        ensure_windpy(auto_fix=True, verbose=True)
    except ImportError:
        # setup_windpy.py 不在同目录时跳过（Windows 等场景）
        pass
    except RuntimeError as e:
        print(f"[wind_server] WindPy 环境配置失败: {e}", file=sys.stderr, flush=True)
        sys.exit(1)

    # 先建立 Wind 连接
    print(f"[wind_server] Connecting to Wind...", flush=True)
    try:
        _ensure_connected()
        print(f"[wind_server] Wind connected.", flush=True)
    except Exception as e:
        print(f"[wind_server] Wind connect failed: {e}", file=sys.stderr, flush=True)
        sys.exit(1)

    server = HTTPServer((args.host, args.port), WindHandler)
    print(f"[wind_server] Listening on http://{args.host}:{args.port}", flush=True)
    print(f"[wind_server] PID={os.getpid()}, pid_file={pid_file}", flush=True)

    def _shutdown(sig, frame):
        print(f"\n[wind_server] Shutting down...", flush=True)
        threading.Thread(target=server.shutdown, daemon=True).start()

    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    try:
        server.serve_forever()
    finally:
        if _w and _w.isconnected():
            _w.stop()
        if os.path.exists(pid_file):
            os.remove(pid_file)
        print("[wind_server] Stopped.", flush=True)


if __name__ == "__main__":
    main()
