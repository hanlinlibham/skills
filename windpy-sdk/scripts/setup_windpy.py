#!/usr/bin/env python3
"""
macOS WindPy 环境自动检测与配置。

在 macOS 上，Wind API 客户端以 .app 形式安装，但 WindPy.py 不会
自动注册到系统 Python 的 site-packages。本模块自动完成以下检测与修复：

  1. Wind API.app 是否已安装
  2. Wind API.app 进程是否正在运行
  3. WindPy.py 是否可 import
  4. 若不可 import，自动创建 symlink 到 site-packages
  5. ~/.Wind 配置目录是否已正确链接

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

import os
import platform
import site
import subprocess
import sys


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
WIND_APP_PATH = "/Applications/Wind API.app"
WIND_WINDPY_SOURCE = os.path.join(WIND_APP_PATH, "Contents", "python", "WindPy.py")
WIND_DOT_DIR_CONTAINER = os.path.expanduser(
    "~/Library/Containers/com.wind.mac.api/Data/.Wind"
)
WIND_DOT_DIR_HOME = os.path.expanduser("~/.Wind")

WIND_PROCESS_NAMES = ["Wind API", "com.wind.mac.api"]


# ---------------------------------------------------------------------------
# 检测函数
# ---------------------------------------------------------------------------

def is_macos() -> bool:
    """当前系统是否为 macOS。"""
    return platform.system() == "Darwin"


def wind_app_installed() -> bool:
    """Wind API.app 是否存在于 /Applications。"""
    return os.path.isdir(WIND_APP_PATH)


def wind_app_running() -> bool:
    """Wind API.app 进程是否正在运行。"""
    try:
        out = subprocess.check_output(["pgrep", "-fl", "Wind API"], text=True, stderr=subprocess.DEVNULL)
        return bool(out.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    # 备用方案: 检查 com.wind.mac.api
    try:
        out = subprocess.check_output(["pgrep", "-f", "com.wind.mac.api"], text=True, stderr=subprocess.DEVNULL)
        return bool(out.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def windpy_source_exists() -> bool:
    """Wind API.app 内部的 WindPy.py 是否存在。"""
    return os.path.isfile(WIND_WINDPY_SOURCE)


def windpy_importable() -> bool:
    """WindPy 是否可以在当前 Python 环境中 import。"""
    try:
        import importlib
        importlib.import_module("WindPy")
        return True
    except ImportError:
        return False


def _find_windpy_location() -> str | None:
    """查找 WindPy.py 在 sys.path 中的实际位置。"""
    for p in sys.path:
        candidate = os.path.join(p, "WindPy.py")
        if os.path.exists(candidate):
            return candidate
    return None


def wind_dot_dir_ok() -> bool:
    """~/.Wind 是否正确链接到容器目录。"""
    if not os.path.exists(WIND_DOT_DIR_HOME):
        return False
    if os.path.islink(WIND_DOT_DIR_HOME):
        target = os.readlink(WIND_DOT_DIR_HOME)
        return target == WIND_DOT_DIR_CONTAINER
    # 如果是真实目录（非 symlink）也算可用
    return os.path.isdir(WIND_DOT_DIR_HOME)


def verify_wind_connection() -> tuple[bool, str]:
    """
    验证 WindPy 能否真正连接并查询数据。

    返回 (success, message)。
    """
    try:
        from WindPy import w

        ret = w.start()
        if not w.isconnected():
            return False, f"w.start() 返回但未连接: {ret}"

        # 测试查询: 获取平安银行证券名称
        ret = w.wss("000001.SZ", "sec_name", "")
        if hasattr(ret, "ErrorCode") and ret.ErrorCode != 0:
            w.stop()
            return False, f"测试查询失败 (ErrorCode={ret.ErrorCode}): {ret.Data}"

        # 提取结果
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
# 修复函数
# ---------------------------------------------------------------------------

def _link_windpy_to_site_packages() -> list[str]:
    """
    创建 WindPy.py 的 symlink 到 user site-packages 和 global site-packages。
    返回成功创建的路径列表。
    """
    linked = []

    # User site-packages
    user_sp = site.getusersitepackages()
    if user_sp:
        os.makedirs(user_sp, exist_ok=True)
        dst = os.path.join(user_sp, "WindPy.py")
        _force_symlink(WIND_WINDPY_SOURCE, dst)
        linked.append(dst)

    # Global site-packages (可能需要权限)
    try:
        global_sps = site.getsitepackages()
        if global_sps:
            dst = os.path.join(global_sps[0], "WindPy.py")
            _force_symlink(WIND_WINDPY_SOURCE, dst)
            linked.append(dst)
    except (PermissionError, OSError) as e:
        # global site-packages 可能需要 sudo，跳过
        pass

    return linked


def _link_wind_dot_dir() -> bool:
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
# 诊断报告
# ---------------------------------------------------------------------------

class DiagResult:
    """诊断结果。"""

    def __init__(self):
        self.is_macos: bool = False
        self.app_installed: bool = False
        self.app_running: bool = False
        self.windpy_source_exists: bool = False
        self.windpy_importable: bool = False
        self.windpy_location: str | None = None
        self.dot_wind_ok: bool = False
        self.verified: bool = False
        self.verify_message: str = ""
        self.python_version: str = sys.version
        self.python_executable: str = sys.executable
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.fixed: list[str] = []

    @property
    def ready(self) -> bool:
        """WindPy 是否可用。"""
        return self.windpy_importable and self.is_macos and self.app_installed

    def summary(self) -> str:
        lines = [
            "=" * 60,
            "WindPy macOS 环境诊断报告",
            "=" * 60,
            f"  Python 版本    : {self.python_version.split()[0]}",
            f"  Python 路径    : {self.python_executable}",
            f"  操作系统       : {'macOS' if self.is_macos else platform.system()}",
            "",
            "检测项目:",
            f"  [{'OK' if self.app_installed else 'FAIL'}] Wind API.app 已安装",
            f"  [{'OK' if self.app_running else 'WARN'}] Wind API.app 正在运行",
            f"  [{'OK' if self.windpy_source_exists else 'FAIL'}] WindPy.py 源文件存在",
            f"  [{'OK' if self.windpy_importable else 'FAIL'}] WindPy 可 import",
            f"  [{'OK' if self.dot_wind_ok else 'WARN'}] ~/.Wind 配置目录",
        ]

        if self.windpy_location:
            lines.append(f"  WindPy 位置     : {self.windpy_location}")

        # 连接验证结果
        if self.verified:
            lines.append(f"  [ OK ] 连接验证: {self.verify_message}")
        elif self.verify_message:
            lines.append(f"  [FAIL] 连接验证: {self.verify_message}")

        if self.fixed:
            lines.append("")
            lines.append("已修复:")
            for f in self.fixed:
                lines.append(f"  [FIXED] {f}")

        if self.warnings:
            lines.append("")
            lines.append("警告:")
            for w in self.warnings:
                lines.append(f"  [WARN] {w}")

        if self.errors:
            lines.append("")
            lines.append("错误:")
            for e in self.errors:
                lines.append(f"  [ERROR] {e}")

        lines.append("")
        status = "READY" if self.ready else "NOT READY"
        lines.append(f"状态: {status}")
        lines.append("=" * 60)
        return "\n".join(lines)


def diagnose(fix: bool = False, verify: bool = False) -> DiagResult:
    """
    运行完整诊断。

    Args:
        fix: 为 True 时自动修复可修复的问题。
        verify: 为 True 时在环境就绪后尝试连接 Wind 并执行测试查询。

    Returns:
        DiagResult 诊断结果。
    """
    r = DiagResult()

    # 1. 平台检查
    r.is_macos = is_macos()
    if not r.is_macos:
        r.errors.append("非 macOS 系统，此脚本仅适用于 macOS")
        return r

    # 2. Wind API.app 安装检查
    r.app_installed = wind_app_installed()
    if not r.app_installed:
        r.errors.append(
            f"Wind API.app 未安装。请从 Wind 官网下载并安装到 {WIND_APP_PATH}"
        )
        return r

    # 3. Wind API.app 进程检查
    r.app_running = wind_app_running()
    if not r.app_running:
        r.warnings.append(
            "Wind API.app 未运行。请先打开 Wind API 客户端并登录。"
            "启动命令: open '/Applications/Wind API.app'"
        )

    # 4. WindPy.py 源文件检查
    r.windpy_source_exists = windpy_source_exists()
    if not r.windpy_source_exists:
        r.errors.append(
            f"WindPy.py 不存在于 {WIND_WINDPY_SOURCE}。"
            "Wind API.app 安装可能不完整，请重新安装。"
        )
        return r

    # 5. WindPy 可导入检查
    r.windpy_importable = windpy_importable()
    r.windpy_location = _find_windpy_location()

    if not r.windpy_importable and fix:
        # 尝试修复: 创建 symlink
        linked = _link_windpy_to_site_packages()
        for path in linked:
            r.fixed.append(f"创建 symlink: {path} -> {WIND_WINDPY_SOURCE}")

        # 重新检测
        # 因为 symlink 已创建，需要刷新 importlib 缓存
        import importlib
        importlib.invalidate_caches()
        r.windpy_importable = windpy_importable()
        r.windpy_location = _find_windpy_location()

        if not r.windpy_importable:
            r.errors.append(
                "自动修复后 WindPy 仍无法导入。"
                "请手动检查 site-packages 路径和 symlink 权限。"
            )
    elif not r.windpy_importable:
        r.errors.append(
            "WindPy 无法导入。运行 `python setup_windpy.py --fix` 自动修复，"
            "或手动创建 symlink:\n"
            f"  ln -sf '{WIND_WINDPY_SOURCE}' "
            f"'{os.path.join(site.getusersitepackages(), 'WindPy.py')}'"
        )

    # 6. ~/.Wind 配置目录检查
    r.dot_wind_ok = wind_dot_dir_ok()
    if not r.dot_wind_ok and fix:
        if os.path.isdir(WIND_DOT_DIR_CONTAINER):
            success = _link_wind_dot_dir()
            if success:
                r.fixed.append(
                    f"创建 symlink: {WIND_DOT_DIR_HOME} -> {WIND_DOT_DIR_CONTAINER}"
                )
                r.dot_wind_ok = True
            else:
                r.warnings.append(
                    f"无法创建 ~/.Wind symlink。"
                    f"容器目录不存在: {WIND_DOT_DIR_CONTAINER}"
                )
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
            r.warnings.append(
                "~/.Wind 不存在。请先打开 Wind API.app 并登录，"
                "系统会自动创建配置目录。"
            )

    # 7. 连接验证（仅在 WindPy 可导入且 Wind 客户端正在运行时执行）
    if r.windpy_importable and r.app_running and verify:
        r.verified, r.verify_message = verify_wind_connection()
        if not r.verified:
            r.warnings.append(f"连接验证失败: {r.verify_message}")

    return r


# ---------------------------------------------------------------------------
# 对外接口 — 供 wind_server.py 调用
# ---------------------------------------------------------------------------

def ensure_windpy(auto_fix: bool = True, verbose: bool = True):
    """
    确保 WindPy 可用。macOS 下自动检测并修复；非 macOS 跳过。

    Args:
        auto_fix: 自动修复（创建 symlink）。
        verbose:  打印诊断信息。

    Raises:
        RuntimeError: WindPy 无法使用且无法修复。
    """
    if not is_macos():
        # 非 macOS: 不做额外处理，让后续 import 自然报错
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
        description="macOS WindPy 环境检测与配置工具"
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="自动修复（创建 symlink 到 site-packages，链接 ~/.Wind）",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="仅检测，不修复（默认行为）",
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="修复后连接 Wind 并执行测试查询（w.wss 000001.SZ sec_name）",
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
