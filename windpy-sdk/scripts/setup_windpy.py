#!/usr/bin/env python3
"""
WindPy 环境检测与配置（macOS + Windows）。

核心功能: 检查 WindPy 是否可 import，不可时尝试自动修复。

macOS:
  WindPy.py 在 Wind API.app 内部，不在 site-packages。
  修复方式: 创建 symlink 到 site-packages + 链接 ~/.Wind 配置。

Windows:
  Wind 终端安装时会将 WindPy 注册到 Python 路径。
  如果不可 import，说明安装不完整，提示用户重新配置。

用法:
    # 作为模块
    from setup_windpy import ensure_windpy
    ensure_windpy()
    from WindPy import w

    # 作为脚本
    python setup_windpy.py           # 检测
    python setup_windpy.py --fix     # 检测 + 修复
    python setup_windpy.py --verify  # 检测 + 连接验证
"""

import os
import platform
import site
import sys


# ---------------------------------------------------------------------------
# macOS 常量
# ---------------------------------------------------------------------------
WIND_APP_PATH = "/Applications/Wind API.app"
WIND_WINDPY_SOURCE_MAC = os.path.join(WIND_APP_PATH, "Contents", "python", "WindPy.py")
WIND_DOT_DIR_CONTAINER = os.path.expanduser(
    "~/Library/Containers/com.wind.mac.api/Data/.Wind"
)
WIND_DOT_DIR_HOME = os.path.expanduser("~/.Wind")


# ---------------------------------------------------------------------------
# 平台判断
# ---------------------------------------------------------------------------

def is_macos() -> bool:
    return platform.system() == "Darwin"


def is_windows() -> bool:
    return platform.system() == "Windows"


# ---------------------------------------------------------------------------
# 通用检测
# ---------------------------------------------------------------------------

def windpy_importable() -> bool:
    """WindPy 是否可 import。"""
    try:
        import importlib
        importlib.import_module("WindPy")
        return True
    except ImportError:
        return False


def _find_windpy_location() -> str | None:
    """查找 WindPy 在 sys.path 中的实际路径。"""
    for p in sys.path:
        for name in ("WindPy.py", "WindPy.pyd", "WindPy.so"):
            candidate = os.path.join(p, name)
            if os.path.exists(candidate):
                return candidate
    return None


def verify_wind_connection() -> tuple[bool, str]:
    """连接 Wind 并执行测试查询。返回 (success, message)。"""
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
# macOS: symlink 修复
# ---------------------------------------------------------------------------

def _force_symlink(src: str, dst: str):
    """强制创建 symlink，已存在则替换。"""
    if os.path.islink(dst) or os.path.isfile(dst):
        os.remove(dst)
    os.symlink(src, dst)


def _mac_fix_windpy_import() -> list[str]:
    """创建 WindPy.py symlink 到 site-packages。返回创建的路径列表。"""
    if not os.path.isfile(WIND_WINDPY_SOURCE_MAC):
        return []

    linked = []

    # User site-packages
    user_sp = site.getusersitepackages()
    if user_sp:
        os.makedirs(user_sp, exist_ok=True)
        dst = os.path.join(user_sp, "WindPy.py")
        _force_symlink(WIND_WINDPY_SOURCE_MAC, dst)
        linked.append(dst)

    # Global site-packages
    try:
        global_sps = site.getsitepackages()
        if global_sps:
            dst = os.path.join(global_sps[0], "WindPy.py")
            _force_symlink(WIND_WINDPY_SOURCE_MAC, dst)
            linked.append(dst)
    except (PermissionError, OSError):
        pass

    return linked


def _mac_fix_dot_wind() -> bool:
    """创建 ~/.Wind -> 容器目录的 symlink。"""
    if not os.path.isdir(WIND_DOT_DIR_CONTAINER):
        return False
    _force_symlink(WIND_DOT_DIR_CONTAINER, WIND_DOT_DIR_HOME)
    return True


def _mac_dot_wind_ok() -> bool:
    """~/.Wind 是否正确链接。"""
    if not os.path.exists(WIND_DOT_DIR_HOME):
        return False
    if os.path.islink(WIND_DOT_DIR_HOME):
        return os.readlink(WIND_DOT_DIR_HOME) == WIND_DOT_DIR_CONTAINER
    return os.path.isdir(WIND_DOT_DIR_HOME)


# ---------------------------------------------------------------------------
# 诊断结果
# ---------------------------------------------------------------------------

class DiagResult:
    def __init__(self):
        self.platform: str = platform.system()
        self.windpy_importable: bool = False
        self.windpy_location: str | None = None
        self.dot_wind_ok: bool = True
        self.verified: bool = False
        self.verify_message: str = ""
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.fixed: list[str] = []

    @property
    def ready(self) -> bool:
        return self.windpy_importable

    def summary(self) -> str:
        plat = "macOS" if self.platform == "Darwin" else self.platform
        lines = [
            "=" * 60,
            f"WindPy 环境诊断 ({plat})",
            "=" * 60,
            f"  Python: {sys.version.split()[0]} ({sys.executable})",
            "",
            f"  [{'OK' if self.windpy_importable else 'FAIL'}] WindPy 可 import",
        ]

        if self.windpy_location:
            lines.append(f"       位置: {self.windpy_location}")

        if self.platform == "Darwin":
            lines.append(f"  [{'OK' if self.dot_wind_ok else 'WARN'}] ~/.Wind 配置目录")

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

def diagnose(fix: bool = False, verify: bool = False) -> DiagResult:
    r = DiagResult()

    # 1. 核心检查: WindPy 是否可 import
    r.windpy_importable = windpy_importable()
    r.windpy_location = _find_windpy_location()

    # 2. 可 import → 跳到验证
    if r.windpy_importable:
        pass

    # 3. 不可 import → 平台特定修复
    elif is_macos():
        if not os.path.isdir(WIND_APP_PATH):
            r.errors.append(f"Wind API.app 未安装 ({WIND_APP_PATH})")
        elif not os.path.isfile(WIND_WINDPY_SOURCE_MAC):
            r.errors.append(f"WindPy.py 不存在于 {WIND_WINDPY_SOURCE_MAC}，安装可能不完整")
        elif fix:
            linked = _mac_fix_windpy_import()
            for path in linked:
                r.fixed.append(f"symlink: {path} -> {WIND_WINDPY_SOURCE_MAC}")
            import importlib
            importlib.invalidate_caches()
            r.windpy_importable = windpy_importable()
            r.windpy_location = _find_windpy_location()
            if not r.windpy_importable:
                r.errors.append("创建 symlink 后仍无法导入，请检查权限")
        else:
            r.errors.append(
                "WindPy 无法导入。运行 --fix 自动修复，或手动:\n"
                f"  ln -sf '{WIND_WINDPY_SOURCE_MAC}' "
                f"'{os.path.join(site.getusersitepackages(), 'WindPy.py')}'"
            )

    elif is_windows():
        r.errors.append(
            "WindPy 无法导入。请检查:\n"
            "  1. Wind 金融终端是否已安装\n"
            "  2. 安装时是否勾选了「Python API」组件\n"
            "  3. 当前 Python 版本是否与 Wind 支持的版本一致\n"
            "  修复: 打开 Wind 终端 → 帮助 → 修复 Python 接口"
        )

    else:
        r.errors.append(f"不支持的平台: {r.platform}")
        return r

    # 4. macOS: ~/.Wind 配置目录
    if is_macos():
        r.dot_wind_ok = _mac_dot_wind_ok()
        if not r.dot_wind_ok and fix:
            if _mac_fix_dot_wind():
                r.fixed.append(f"symlink: {WIND_DOT_DIR_HOME} -> {WIND_DOT_DIR_CONTAINER}")
                r.dot_wind_ok = True
            else:
                r.warnings.append("~/.Wind 配置目录不存在，请先打开 Wind API.app 并登录一次")
        elif not r.dot_wind_ok:
            r.warnings.append("~/.Wind 未正确链接，运行 --fix 修复")

    # 5. 连接验证
    if r.windpy_importable and verify:
        r.verified, r.verify_message = verify_wind_connection()
        if not r.verified:
            r.warnings.append(f"连接验证失败: {r.verify_message}")

    return r


# ---------------------------------------------------------------------------
# 对外接口
# ---------------------------------------------------------------------------

def ensure_windpy(auto_fix: bool = True, verbose: bool = True):
    """
    确保 WindPy 可用。不可用时自动修复（macOS: symlink）。

    Raises:
        RuntimeError: WindPy 无法使用且无法修复。
    """
    if windpy_importable():
        if verbose:
            loc = _find_windpy_location()
            print(f"[setup_windpy] WindPy 已就绪 ({loc})", flush=True)
        return

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
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="WindPy 环境检测与配置")
    parser.add_argument("--fix", action="store_true", help="自动修复")
    parser.add_argument("--check", action="store_true", help="仅检测不修复")
    parser.add_argument("--verify", action="store_true", help="连接 Wind 并执行测试查询")
    parser.add_argument("--quiet", action="store_true", help="静默模式，仅在失败时输出")
    args = parser.parse_args()

    do_fix = args.fix and not args.check
    result = diagnose(fix=do_fix, verify=args.verify or args.fix)

    if not args.quiet or not result.ready:
        print(result.summary())

    sys.exit(0 if result.ready else 1)


if __name__ == "__main__":
    main()
