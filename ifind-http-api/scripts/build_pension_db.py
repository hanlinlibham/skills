#!/usr/bin/env python3
"""
养老金产品 SQLite 数据库构建脚本

从 iFinD HTTP API 批量获取养老金产品基础信息并存入 SQLite 数据库。
数据源：ifind/基础信息数据.md 中的 1722 个 .YLJ 产品代码。

用法:
    # 使用环境变量
    export IFIND_REFRESH_TOKEN="your_refresh_token"
    python build_pension_db.py

    # 或直接传参
    python build_pension_db.py --refresh-token "your_refresh_token"

    # 指定输出路径
    python build_pension_db.py --db-path /path/to/pension_products.db

    # 从自定义源文件提取代码
    python build_pension_db.py --source /path/to/基础信息数据.md
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path

import requests

# ---------- 配置 ----------

BASE_URL = "https://quantapi.51ifind.com/api/v1"
BATCH_SIZE = 50  # 每批查询的代码数量，避免请求过大
RETRY_MAX = 3
RETRY_DELAY = 2  # 秒

# 管理人前缀映射
MANAGER_MAP = {
    "00": "全国社保基金理事会", "02": "博时基金", "05": "大成基金",
    "07": "工银瑞信", "10": "海富通基金", "11": "华夏基金",
    "15": "嘉实基金", "18": "南方基金", "20": "鹏华基金",
    "48": "易方达基金", "51": "银华基金",
    "CJ": "长江养老", "CL": "长城人寿", "HT": "华泰资产",
    "JX": "建信养老金", "LC": "长量基金", "PA": "平安养老",
    "RB": "人保资产", "TP": "太平养老", "TZ": "泰康资产",
    "XH": "新华养老", "ZJ": "中金公司", "ZX": "中信证券",
}

# 产品类型映射
TYPE_MAP = {
    "A": "权益型", "B": "混合型", "C": "债券型", "D": "货币型",
}

BOND_SUBTYPE_MAP = {
    "Ca": "普通债券", "Cb": "信用债/定制类", "Cc": "债券C子类",
    "Cd": "债券D子类", "Ce": "债券E子类",
    "Cf": "定制固收F", "Cg": "定制固收G", "Ch": "债券H子类",
}


# ---------- 工具函数 ----------

def parse_code(code: str) -> dict:
    """解析养老金产品代码，提取管理人前缀、产品类型等。"""
    base = code.replace(".YLJ", "")

    # 尝试匹配：先匹配2字母前缀（CJ/CL/HT等），再匹配2数字前缀
    manager_prefix = None
    product_type = None
    bond_subtype = None

    for prefix in sorted(MANAGER_MAP.keys(), key=len, reverse=True):
        if base.startswith(prefix):
            manager_prefix = prefix
            remainder = base[len(prefix):]
            break
    else:
        # 未匹配到已知前缀，取前2字符
        manager_prefix = base[:2]
        remainder = base[2:]

    # 从remainder提取产品类型
    if remainder:
        first_char = remainder[0].upper()
        if first_char in TYPE_MAP:
            product_type = first_char
            if first_char == "C" and len(remainder) > 1:
                second_char = remainder[1]
                if second_char.isalpha():
                    bond_subtype = f"C{second_char}"
        else:
            product_type = "未知"

    return {
        "manager_prefix": manager_prefix,
        "manager_name": MANAGER_MAP.get(manager_prefix, "未知"),
        "product_type": product_type or "未知",
        "product_type_name": TYPE_MAP.get(product_type, "未知"),
        "bond_subtype": bond_subtype,
        "bond_subtype_name": BOND_SUBTYPE_MAP.get(bond_subtype),
    }


def extract_codes_from_md(filepath: str) -> list[str]:
    """从基础信息数据.md中提取所有 .YLJ 产品代码。"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    codes = sorted(set(re.findall(r"[A-Za-z0-9]+\.YLJ", content)))
    print(f"从 {filepath} 提取到 {len(codes)} 个产品代码")
    return codes


def get_access_token(refresh_token: str) -> str:
    """获取 iFinD access_token。"""
    resp = requests.post(
        f"{BASE_URL}/get_access_token",
        headers={"Content-Type": "application/json", "refresh_token": refresh_token},
    )
    data = resp.json()
    if "data" in data and "access_token" in data["data"]:
        print("access_token 获取成功")
        return data["data"]["access_token"]
    raise RuntimeError(f"获取 access_token 失败: {data}")


def fetch_basic_data(access_token: str, codes: list[str], indicators: list[dict]) -> dict:
    """调用 basic_data_service 获取基础数据，带重试。"""
    headers = {"Content-Type": "application/json", "access_token": access_token}
    params = {
        "codes": ",".join(codes),
        "indipara": indicators,
    }

    for attempt in range(RETRY_MAX):
        try:
            resp = requests.post(
                f"{BASE_URL}/basic_data_service",
                json=params,
                headers=headers,
                timeout=30,
            )
            data = resp.json()
            if data.get("errorcode") == 0:
                return data
            print(f"  API 错误 {data.get('errorcode')}: {data.get('errmsg', '')}")
            if data.get("errorcode") in (-1020, -1021):
                # 流量限制，等待后重试
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            return data
        except requests.exceptions.RequestException as e:
            print(f"  请求异常 (尝试 {attempt+1}/{RETRY_MAX}): {e}")
            time.sleep(RETRY_DELAY * (attempt + 1))

    return {"errorcode": -9999, "errmsg": "max retries exceeded"}


# ---------- 数据库操作 ----------

def create_db(db_path: str) -> sqlite3.Connection:
    """创建 SQLite 数据库和表结构。"""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pension_products (
            code TEXT PRIMARY KEY,
            name TEXT,
            official_name TEXT,
            manager_prefix TEXT,
            manager_name TEXT,
            product_type TEXT,
            product_type_name TEXT,
            bond_subtype TEXT,
            bond_subtype_name TEXT,
            establishment_date TEXT,
            expiry_date TEXT,
            last_updated TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_name ON pension_products(name)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_manager ON pension_products(manager_prefix)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_type ON pension_products(product_type)
    """)
    # 全文搜索虚拟表
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS pension_fts USING fts5(
            code, name, official_name, manager_name, product_type_name,
            content='pension_products',
            content_rowid='rowid'
        )
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS pension_ai AFTER INSERT ON pension_products BEGIN
            INSERT INTO pension_fts(rowid, code, name, official_name, manager_name, product_type_name)
            VALUES (new.rowid, new.code, new.name, new.official_name, new.manager_name, new.product_type_name);
        END
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS pension_ad AFTER DELETE ON pension_products BEGIN
            INSERT INTO pension_fts(pension_fts, rowid, code, name, official_name, manager_name, product_type_name)
            VALUES ('delete', old.rowid, old.code, old.name, old.official_name, old.manager_name, old.product_type_name);
        END
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS pension_au AFTER UPDATE ON pension_products BEGIN
            INSERT INTO pension_fts(pension_fts, rowid, code, name, official_name, manager_name, product_type_name)
            VALUES ('delete', old.rowid, old.code, old.name, old.official_name, old.manager_name, old.product_type_name);
            INSERT INTO pension_fts(rowid, code, name, official_name, manager_name, product_type_name)
            VALUES (new.rowid, new.code, new.name, new.official_name, new.manager_name, new.product_type_name);
        END
    """)
    conn.commit()
    return conn


def upsert_products(conn: sqlite3.Connection, records: list[dict]):
    """批量插入或更新产品记录。"""
    conn.executemany("""
        INSERT INTO pension_products (
            code, name, official_name, manager_prefix, manager_name,
            product_type, product_type_name, bond_subtype, bond_subtype_name,
            establishment_date, expiry_date, last_updated
        ) VALUES (
            :code, :name, :official_name, :manager_prefix, :manager_name,
            :product_type, :product_type_name, :bond_subtype, :bond_subtype_name,
            :establishment_date, :expiry_date, datetime('now', 'localtime')
        )
        ON CONFLICT(code) DO UPDATE SET
            name = excluded.name,
            official_name = excluded.official_name,
            establishment_date = excluded.establishment_date,
            expiry_date = excluded.expiry_date,
            last_updated = excluded.last_updated
    """, records)
    conn.commit()


# ---------- 主流程 ----------

def build_database(codes: list[str], access_token: str, db_path: str, batch_size: int = BATCH_SIZE):
    """主构建流程：批量获取数据并写入数据库。"""
    conn = create_db(db_path)

    # 指标列表
    indicators = [
        {"indicator": "ths_fund_short_name_fund", "indiparams": [""]},
        {"indicator": "ths_fund_official_short_name_fund", "indiparams": [""]},
        {"indicator": "ths_fund_establishment_date_fund", "indiparams": [""]},
        {"indicator": "ths_fund_expiry_date_fund", "indiparams": [""]},
    ]

    total = len(codes)
    success_count = 0
    error_count = 0

    for i in range(0, total, batch_size):
        batch = codes[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size
        print(f"[{batch_num}/{total_batches}] 获取 {len(batch)} 个产品数据...")

        data = fetch_basic_data(access_token, batch, indicators)

        if data.get("errorcode") != 0:
            print(f"  批次失败: {data.get('errmsg', '未知错误')}")
            error_count += len(batch)
            continue

        # 解析返回数据
        tables = data.get("tables", [])
        records = []
        for table in tables:
            code = table.get("thscode", "")
            row = table.get("table", {})

            # basic_data_service 返回的 table 是 {indicator: [value]} 格式
            name = _extract_value(row, "ths_fund_short_name_fund")
            official_name = _extract_value(row, "ths_fund_official_short_name_fund")
            est_date = _extract_value(row, "ths_fund_establishment_date_fund")
            exp_date = _extract_value(row, "ths_fund_expiry_date_fund")

            parsed = parse_code(code)
            records.append({
                "code": code,
                "name": name,
                "official_name": official_name,
                "establishment_date": est_date,
                "expiry_date": exp_date,
                **parsed,
            })

        if records:
            upsert_products(conn, records)
            success_count += len(records)
            print(f"  写入 {len(records)} 条记录")

        # 请求间隔，避免触发限流
        if i + batch_size < total:
            time.sleep(0.5)

    conn.close()
    print(f"\n构建完成: {db_path}")
    print(f"  成功: {success_count}, 失败: {error_count}, 总计: {total}")


def _extract_value(table: dict, indicator: str):
    """从 basic_data_service 返回的 table 中提取指标值。"""
    vals = table.get(indicator, [])
    if vals and len(vals) > 0:
        v = vals[0]
        if v and str(v).strip() and str(v).strip() != "--":
            return str(v).strip()
    return None


def main():
    parser = argparse.ArgumentParser(description="构建养老金产品 SQLite 数据库")
    parser.add_argument("--refresh-token", default=os.environ.get("IFIND_REFRESH_TOKEN"),
                        help="iFinD refresh_token (或设置 IFIND_REFRESH_TOKEN 环境变量)")
    parser.add_argument("--access-token", default=os.environ.get("IFIND_ACCESS_TOKEN"),
                        help="直接传入 access_token 跳过认证 (或设置 IFIND_ACCESS_TOKEN)")
    parser.add_argument("--source", default=None,
                        help="基础信息数据.md 文件路径")
    parser.add_argument("--db-path", default=None,
                        help="SQLite 数据库输出路径")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE,
                        help=f"每批查询代码数 (默认 {BATCH_SIZE})")
    args = parser.parse_args()

    # 确定源文件路径
    if args.source:
        source_path = args.source
    else:
        # 默认查找路径
        candidates = [
            Path(__file__).parent.parent.parent.parent / "ifind" / "基础信息数据.md",
            Path.home() / "Space" / "ifind" / "基础信息数据.md",
        ]
        source_path = next((str(p) for p in candidates if p.exists()), None)
        if not source_path:
            print("错误: 找不到 基础信息数据.md，请使用 --source 指定路径")
            sys.exit(1)

    # 确定数据库路径
    if args.db_path:
        db_path = args.db_path
    else:
        db_path = str(Path(__file__).parent.parent / "data" / "pension_products.db")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # 提取代码
    codes = extract_codes_from_md(source_path)
    if not codes:
        print("错误: 未提取到任何产品代码")
        sys.exit(1)

    # 获取 access_token
    access_token = args.access_token
    if not access_token:
        if not args.refresh_token:
            print("错误: 需要提供 --refresh-token 或设置 IFIND_REFRESH_TOKEN 环境变量")
            sys.exit(1)
        access_token = get_access_token(args.refresh_token)

    # 构建数据库
    build_database(codes, access_token, db_path, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
