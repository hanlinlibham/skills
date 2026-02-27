#!/usr/bin/env python3
"""
WindPy 环境自动检测与配置（macOS + Windows）。

macOS:
  Wind API 客户端以 .app 形式安装，WindPy.py 不会自动注册到系统
  Python 的 site-packages。本模块自动创建 symlink 并链接 ~/.Wind 配置。

Windows:
  Wind 金融终端安装后，WindPy.pyd 通常在 Wind 安装目录下，但不一定
  在 sys.path 中。本模块自动搜索 WindPy.pyd 并通过 .pth 文件注册。

检测项目:
  1. Wind 终端是否已安装
  2. Wind 终端进程是否正在运行
  3. WindPy 是否可 import
  4. 若不可 import，自动修复（macOS: symlink / Windows: .pth）
  5. 配置目录检查（macOS: ~/.Wind）

用法:
    # 作为模块调用 — 静默检测，失败抛异常
    from setup_windpy import ensure_windpy

    ensure_windpy()          # 自动检测 + 修复
    from WindPy import w     # 此时可安全导入

    # 作为脚本运行 — 打印诊断信息
    python setup_windpy.py
    python setup_windpy.py --fix     # 检测 + 自动修复
    python setup_windpy.py --check   # 仅检测不修复
"""

import glob
import os
import platform
import site
import subprocess
import sys


# ---------------------------------------------------------------------------
# 常量 — macOS
# ---------------------------------------------------------------------------
WIND_APP_PATH = "/Applications/Wind API.app"
WIND_WINDPY_SOURCE_MAC = os.path.join(WIND_APP_PATH, "Contents", "python", "WindPy.py")
WIND_DOT_DIR_CONTAINER = os.path.expanduser(
    "~/Library/Containers/com.wind.mac.api/Data/.Wind"
)
WIND_DOT_DIR_HOME = os.path.expanduser("~/.Wind")
WIND_MAC_PROCESS_NAMES = ["Wind API", "com.wind.mac.api"]

# ---------------------------------------------------------------------------
# 常量 — Windows
# ---------------------------------------------------------------------------
# Wind 终端常见安装路径（按优先级排列）
WIND_WIN_SEARCH_ROOTS = [
    os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Wind"),
    os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), "Wind"),
    r"C:\Wind",
    r"D:\Wind",
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Wind") if os.environ.get("LOCALAPPDATA") else "",
]
# 可能包含 WindPy.pyd 的子目录模式
WIND_WIN_WINDPY_PATTERNS = [
    "Wind.NET.Client/WindNET/bin/x64",
    "Wind.NET.Client/WindNET/bin",
    "WindNET/bin/x64",
    "WindNET/bin",
    "Python",
    "python",
]
WIND_WIN_PROCESS_NAMES = ["WindNET.exe", "Wind.exe", "WFT.exe"]

# PTH 文件名（写入 site-packages 使 WindPy 目录自动加入 sys.path）
WIND_PTH_FILENAME = "windpy.pth"


# ---------------------------------------------------------------------------
# 平台检测
# ---------------------------------------------------------------------------

def is_macos() -> bool:
    return platform.system() == "Darwin"


def is_windows() -> bool:
    return platform.system() == "Windows"


# ---------------------------------------------------------------------------
# 通用检测函数
# ---------------------------------------------------------------------------

def windpy_importable() -> bool:
    """WindPy 是否可以在当前 Python 环境中 import。"""
    try:
        import importlib
        importlib.import_module("WindPy")
        return True
    except ImportError:
        return False


def _find_windpy_location() -> str | None:
    """查找 WindPy 在 sys.path 中的实际位置。"""
    for p in sys.path:
        for name in ("WindPy.py", "WindPy.pyd", "WindPy.so"):
            candidate = os.path.join(p, name)
            if os.path.exists(candidate):
                return candidate
    return None


def verify_wind_connection() -> tuple[bool, str]:
    """验证 WindPy 能否真正连接并查询数据。返回 (success, message)。"""
    try:
        from WindPy import w

        ret = w.start()
        if not w.isconnected():
            return False, f"w.start() 返回但未连接: {ret}"

        ret = w.wss("000001.SZ", "sec_name", "")
        if hasattr(ret, "ErrorCode") and ret.ErrorCode != 0:
            w.stop()
            return False, f"测试查询失败 (ErrorCode={ret.ErrorCode}): {ret.Data}"

        sec_name = ""
        if hasattr(ret, "Data") and ret.Data and ret.Data[0]:
            sec_name = str(ret.Data[0][0])

        w.stop()
        return True, f"验证通过 — 000001.SZ = {sec_name}"

    except ImportError:
        return False, "WindPy 导入失败"
    except Exception as e:
        return False, f"验证异常: {e}"


# ---------------------------------------------------------------------------
# macOS 专用检测
# ---------------------------------------------------------------------------

def _mac_app_installed() -> bool:
    """Wind API.app 是否存在于 /Applications。"""
    return os.path.isdir(WIND_APP_PATH)


def _mac_app_running() -> bool:
    """Wind API.app 进程是否正在运行。"""
    for name in WIND_MAC_PROCESS_NAMES:
        try:
            out = subprocess.check_output(
                ["pgrep", "-f", name], text=True, stderr=subprocess.DEVNULL
            )
            if out.strip():
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return False


def _mac_windpy_source_exists() -> bool:
    """Wind API.app 内部的 WindPy.py 是否存在。"""
    return os.path.isfile(WIND_WINDPY_SOURCE_MAC)


def _mac_dot_wind_ok() -> bool:
    """~/.Wind 是否正确链接到容器目录。"""
    if not os.path.exists(WIND_DOT_DIR_HOME):
        return False
    if os.path.islink(WIND_DOT_DIR_HOME):
        target = os.readlink(WIND_DOT_DIR_HOME)
        return target == WIND_DOT_DIR_CONTAINER
    return os.path.isdir(WIND_DOT_DIR_HOME)


# ---------------------------------------------------------------------------
# macOS 专用修复
# ---------------------------------------------------------------------------

def _mac_link_windpy_to_site_packages() -> list[str]:
    """创建 WindPy.py 的 symlink 到 site-packages。返回成功创建的路径列表。"""
    linked = []

    user_sp = site.getusersitepackages()
    if user_sp:
        os.makedirs(user_sp, exist_ok=True)
        dst = os.path.join(user_sp, "WindPy.py")
        _force_symlink(WIND_WINDPY_SOURCE_MAC, dst)
        linked.append(dst)

    try:
        global_sps = site.getsitepackages()
        if global_sps:
            dst = os.path.join(global_sps[0], "WindPy.py")
            _force_symlink(WIND_WINDPY_SOURCE_MAC, dst)
            linked.append(dst)
    except (PermissionError, OSError):
        pass

    return linked


def _mac_link_dot_wind() -> bool:
    """创建 ~/.Wind -> 容器目录的 symlink。"""
    if not os.path.isdir(WIND_DOT_DIR_CONTAINER):
        return False
    _force_symlink(WIND_DOT_DIR_CONTAINER, WIND_DOT_DIR_HOME)
    return True


def _force_symlink(src: str, dst: str):
    """强制创建 symlink，已存在则替换。"""
    if os.path.islink(dst) or os.path.isfile(dst):
        os.remove(dst)
    os.symlink(src, dst)


# ---------------------------------------------------------------------------
# Windows 专用检测
# ---------------------------------------------------------------------------

def _win_find_wind_install() -> str | None:
    """查找 Wind 终端安装目录。优先使用注册表，回退到路径扫描。"""
    # 方法1: 注册表
    reg_path = _win_find_from_registry()
    if reg_path:
        return reg_path

    # 方法2: 环境变量
    wind_home = os.environ.get("WIND_HOME", "")
    if wind_home and os.path.isdir(wind_home):
        return wind_home

    # 方法3: 扫描常见路径
    for root in WIND_WIN_SEARCH_ROOTS:
        if not root or not os.path.isdir(root):
            continue
        return root

    return None


def _win_find_from_registry() -> str | None:
    """从 Windows 注册表读取 Wind 安装路径。"""
    try:
        import winreg
    except ImportError:
        return None

    reg_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wind Information\WFT"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Wind Information\WFT"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Wind Information\WFT"),
    ]
    for hive, subkey in reg_keys:
        try:
            with winreg.OpenKey(hive, subkey) as key:
                val, _ = winreg.QueryValueEx(key, "InstallPath")
                if val and os.path.isdir(val):
                    return val
        except (OSError, FileNotFoundError):
            continue
    return None


def _win_find_windpy(install_dir: str | None) -> str | None:
    """在 Wind 安装目录中搜索 WindPy.pyd 所在目录。"""
    if not install_dir:
        return None

    # 按已知子目录模式搜索
    for pattern in WIND_WIN_WINDPY_PATTERNS:
        candidate_dir = os.path.join(install_dir, pattern.replace("/", os.sep))
        for ext in ("WindPy.pyd", "WindPy.py"):
            candidate = os.path.join(candidate_dir, ext)
            if os.path.isfile(candidate):
                return candidate_dir

    # 递归搜索（最多2层深度，避免太慢）
    for depth_pattern in ["*/WindPy.pyd", "*/*/WindPy.pyd", "*/WindPy.py", "*/*/WindPy.py"]:
        matches = glob.glob(os.path.join(install_dir, depth_pattern))
        if matches:
            return os.path.dirname(matches[0])

    return None


def _win_terminal_installed(install_dir: str | None) -> bool:
    """Wind 终端是否已安装。"""
    return install_dir is not None and os.path.isdir(install_dir)


def _win_terminal_running() -> bool:
    """Wind 终端进程是否正在运行。"""
    try:
        out = subprocess.check_output(
            ["tasklist", "/FO", "CSV", "/NH"],
            text=True, stderr=subprocess.DEVNULL,
        )
        out_lower = out.lower()
        for name in WIND_WIN_PROCESS_NAMES:
            if name.lower() in out_lower:
                return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return False


# ---------------------------------------------------------------------------
# Windows 专用修复
# ---------------------------------------------------------------------------

def _win_create_pth_file(windpy_dir: str) -> list[str]:
    """
    创建 .pth 文件到 site-packages，使 WindPy 目录自动加入 sys.path。
    返回成功创建的路径列表。
    """
    created = []

    # User site-packages
    user_sp = site.getusersitepackages()
    if user_sp:
        os.makedirs(user_sp, exist_ok=True)
        pth_path = os.path.join(user_sp, WIND_PTH_FILENAME)
        try:
            with open(pth_path, "w", encoding="utf-8") as f:
                f.write(windpy_dir + "\n")
            created.append(pth_path)
        except OSError:
            pass

    # Global site-packages
    try:
        global_sps = site.getsitepackages()
        if global_sps:
            pth_path = os.path.join(global_sps[0], WIND_PTH_FILENAME)
            with open(pth_path, "w", encoding="utf-8") as f:
                f.write(windpy_dir + "\n")
            created.append(pth_path)
    except (PermissionError, OSError):
        pass

    # 立即添加到 sys.path 使当前进程生效
    if windpy_dir not in sys.path:
        sys.path.insert(0, windpy_dir)

    return created


# ---------------------------------------------------------------------------
# 诊断报告
# ---------------------------------------------------------------------------

class DiagResult:
    """诊断结果。"""

    def __init__(self):
        self.platform: str = platform.system()
        self.terminal_installed: bool = False
        self.terminal_running: bool = False
        self.windpy_source_found: bool = False
        self.windpy_source_path: str = ""
        self.windpy_importable: bool = False
        self.windpy_location: str | None = None
        self.dot_wind_ok: bool = True  # Windows 不检查，默认 True
        self.verified: bool = False
        self.verify_message: str = ""
        self.python_version: str = sys.version
        self.python_executable: str = sys.executable
        self.wind_install_dir: str = ""
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.fixed: list[str] = []

    @property
    def ready(self) -> bool:
        """WindPy 是否可用。"""
        return self.windpy_importable and self.terminal_installed

    def summary(self) -> str:
        plat = "macOS" if self.platform == "Darwin" else self.platform
        lines = [
            "=" * 60,
            f"WindPy {plat} 环境诊断报告",
            "=" * 60,
            f"  Python 版本    : {self.python_version.split()[0]}",
            f"  Python 路径    : {self.python_executable}",
            f"  操作系统       : {plat}",
        ]

        if self.wind_install_dir:
            lines.append(f"  Wind 安装目录  : {self.wind_install_dir}")

        lines += [
            "",
            "检测项目:",
            f"  [{'OK' if self.terminal_installed else 'FAIL'}] Wind 终端已安装",
            f"  [{'OK' if self.terminal_running else 'WARN'}] Wind 终端正在运行",
            f"  [{'OK' if self.windpy_source_found else 'FAIL'}] WindPy 源文件存在",
            f"  [{'OK' if self.windpy_importable else 'FAIL'}] WindPy 可 import",
        ]

        # macOS 才显示 ~/.Wind 检测
        if self.platform == "Darwin":
            lines.append(f"  [{'OK' if self.dot_wind_ok else 'WARN'}] ~/.Wind 配置目录")

        if self.windpy_location:
            lines.append(f"  WindPy 位置     : {self.windpy_location}")

        if self.windpy_source_path and not self.windpy_importable:
            lines.append(f"  WindPy 源路径   : {self.windpy_source_path}")

        if self.verified:
            lines.append(f"  [ OK ] 连接验证: {self.verify_message}")
        elif self.verify_message:
            lines.append(f"  [FAIL] 连接验证: {self.verify_message}")

        if self.fixed:
            lines += ["", "已修复:"]
            for f in self.fixed:
                lines.append(f"  [FIXED] {f}")

        if self.warnings:
            lines += ["", "警告:"]
            for w in self.warnings:
                lines.append(f"  [WARN] {w}")

        if self.errors:
            lines += ["", "错误:"]
            for e in self.errors:
                lines.append(f"  [ERROR] {e}")

        lines += ["", f"状态: {'READY' if self.ready else 'NOT READY'}", "=" * 60]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 诊断主流程
# ---------------------------------------------------------------------------

def _diagnose_macos(r: DiagResult, fix: bool, verify: bool):
    """macOS 诊断流程。"""
    # 1. 安装检查
    r.terminal_installed = _mac_app_installed()
    if not r.terminal_installed:
        r.errors.append(f"Wind API.app 未安装。请从 Wind 官网下载并安装到 {WIND_APP_PATH}")
        return

    r.wind_install_dir = WIND_APP_PATH

    # 2. 进程检查
    r.terminal_running = _mac_app_running()
    if not r.terminal_running:
        r.warnings.append(
            "Wind API.app 未运行。请先打开 Wind API 客户端并登录。"
            "启动命令: open '/Applications/Wind API.app'"
        )

    # 3. WindPy 源文件检查
    r.windpy_source_found = _mac_windpy_source_exists()
    r.windpy_source_path = WIND_WINDPY_SOURCE_MAC
    if not r.windpy_source_found:
        r.errors.append(
            f"WindPy.py 不存在于 {WIND_WINDPY_SOURCE_MAC}。"
            "Wind API.app 安装可能不完整，请重新安装。"
        )
        return

    # 4. 可导入检查 + 修复
    r.windpy_importable = windpy_importable()
    r.windpy_location = _find_windpy_location()

    if not r.windpy_importable and fix:
        linked = _mac_link_windpy_to_site_packages()
        for path in linked:
            r.fixed.append(f"创建 symlink: {path} -> {WIND_WINDPY_SOURCE_MAC}")
        import importlib
        importlib.invalidate_caches()
        r.windpy_importable = windpy_importable()
        r.windpy_location = _find_windpy_location()
        if not r.windpy_importable:
            r.errors.append("自动修复后 WindPy 仍无法导入。请手动检查 site-packages 路径和权限。")
    elif not r.windpy_importable:
        r.errors.append(
            "WindPy 无法导入。运行 `python setup_windpy.py --fix` 自动修复，"
            "或手动创建 symlink:\n"
            f"  ln -sf '{WIND_WINDPY_SOURCE_MAC}' "
            f"'{os.path.join(site.getusersitepackages(), 'WindPy.py')}'"
        )

    # 5. ~/.Wind 配置目录
    r.dot_wind_ok = _mac_dot_wind_ok()
    if not r.dot_wind_ok and fix:
        if os.path.isdir(WIND_DOT_DIR_CONTAINER):
            if _mac_link_dot_wind():
                r.fixed.append(f"创建 symlink: {WIND_DOT_DIR_HOME} -> {WIND_DOT_DIR_CONTAINER}")
                r.dot_wind_ok = True
            else:
                r.warnings.append(f"无法创建 ~/.Wind symlink。容器目录不存在: {WIND_DOT_DIR_CONTAINER}")
        else:
            r.warnings.append(
                f"Wind 容器配置目录不存在: {WIND_DOT_DIR_CONTAINER}。"
                "请先打开 Wind API.app 并至少登录一次以生成配置。"
            )
    elif not r.dot_wind_ok:
        if os.path.isdir(WIND_DOT_DIR_CONTAINER):
            r.warnings.append(
                f"~/.Wind 未链接。运行 --fix 自动修复，或手动执行:\n"
                f"  rm -rf ~/.Wind && ln -sf '{WIND_DOT_DIR_CONTAINER}' ~/.Wind"
            )
        else:
            r.warnings.append("~/.Wind 不存在。请先打开 Wind API.app 并登录以生成配置目录。")


def _diagnose_windows(r: DiagResult, fix: bool, verify: bool):
    """Windows 诊断流程。"""
    # 1. 查找 Wind 安装目录
    install_dir = _win_find_wind_install()
    r.terminal_installed = _win_terminal_installed(install_dir)
    r.wind_install_dir = install_dir or ""

    if not r.terminal_installed:
        r.errors.append(
            "未找到 Wind 金融终端。请确认已安装 Wind 终端，"
            "或设置环境变量 WIND_HOME 指向安装目录。\n"
            f"  已搜索路径: {', '.join(p for p in WIND_WIN_SEARCH_ROOTS if p)}"
        )
        return

    # 2. 进程检查
    r.terminal_running = _win_terminal_running()
    if not r.terminal_running:
        r.warnings.append("Wind 终端未运行。请先打开 Wind 金融终端并登录。")

    # 3. 搜索 WindPy.pyd / WindPy.py
    windpy_dir = _win_find_windpy(install_dir)
    r.windpy_source_found = windpy_dir is not None
    r.windpy_source_path = windpy_dir or ""

    if not r.windpy_source_found:
        r.errors.append(
            f"在 Wind 安装目录 {install_dir} 中未找到 WindPy.pyd 或 WindPy.py。\n"
            "请确认 Wind 终端安装完整且已配置 Python API。\n"
            "如果 WindPy 在其他位置，请设置: set PYTHONPATH=<WindPy所在目录>"
        )
        return

    # 4. 可导入检查 + 修复
    r.windpy_importable = windpy_importable()
    r.windpy_location = _find_windpy_location()

    if not r.windpy_importable and fix and windpy_dir:
        created = _win_create_pth_file(windpy_dir)
        for path in created:
            r.fixed.append(f"创建 .pth 文件: {path} (内容: {windpy_dir})")
        import importlib
        importlib.invalidate_caches()
        r.windpy_importable = windpy_importable()
        r.windpy_location = _find_windpy_location()
        if not r.windpy_importable:
            r.errors.append(
                "自动修复后 WindPy 仍无法导入。请手动将以下路径添加到 PYTHONPATH:\n"
                f"  set PYTHONPATH={windpy_dir};%PYTHONPATH%"
            )
    elif not r.windpy_importable:
        r.errors.append(
            "WindPy 无法导入。运行 `python setup_windpy.py --fix` 自动修复，"
            "或手动添加到 PYTHONPATH:\n"
            f"  set PYTHONPATH={windpy_dir};%PYTHONPATH%"
        )


def diagnose(fix: bool = False, verify: bool = False) -> DiagResult:
    """
    运行完整诊断。

    Args:
        fix: 为 True 时自动修复可修复的问题。
        verify: 为 True 时在环境就绪后尝试连接 Wind 并执行测试查询。
    """
    r = DiagResult()

    if is_macos():
        _diagnose_macos(r, fix, verify)
    elif is_windows():
        _diagnose_windows(r, fix, verify)
    else:
        r.errors.append(f"不支持的操作系统: {r.platform}。WindPy 仅支持 macOS 和 Windows。")
        return r

    # 连接验证
    if r.windpy_importable and r.terminal_running and verify:
        r.verified, r.verify_message = verify_wind_connection()
        if not r.verified:
            r.warnings.append(f"连接验证失败: {r.verify_message}")

    return r


# ---------------------------------------------------------------------------
# 对外接口 — 供 wind_client.py / wind_server.py 调用
# ---------------------------------------------------------------------------

def ensure_windpy(auto_fix: bool = True, verbose: bool = True):
    """
    确保 WindPy 可用。自动检测平台并修复。

    Args:
        auto_fix: 自动修复（macOS: 创建 symlink / Windows: 创建 .pth）。
        verbose:  打印诊断信息。

    Raises:
        RuntimeError: WindPy 无法使用且无法修复。
    """
    if not is_macos() and not is_windows():
        return

    # 如果已经能导入，快速返回
    if windpy_importable():
        if verbose:
            loc = _find_windpy_location()
            print(f"[setup_windpy] WindPy 已就绪 ({loc})", flush=True)
        return

    # 需要修复
    if verbose:
        print("[setup_windpy] WindPy 不可导入，开始诊断...", flush=True)

    result = diagnose(fix=auto_fix)

    if verbose:
        print(result.summary(), flush=True)

    if not result.ready:
        errors = "; ".join(result.errors) if result.errors else "未知错误"
        raise RuntimeError(f"WindPy 环境配置失败: {errors}")

    if verbose:
        print("[setup_windpy] WindPy 环境配置完成", flush=True)


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="WindPy 环境检测与配置工具（macOS + Windows）"
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="自动修复（macOS: symlink / Windows: .pth 文件）",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="仅检测，不修复（默认行为）",
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="修复后连接 Wind 并执行测试查询",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="静默模式，仅在失败时输出",
    )
    args = parser.parse_args()

    do_fix = args.fix and not args.check

    result = diagnose(fix=do_fix, verify=args.verify or args.fix)

    if not args.quiet or not result.ready:
        print(result.summary())

    sys.exit(0 if result.ready else 1)


if __name__ == "__main__":
    main()
