#!/usr/bin/env python3
"""
养老金产品 SQLite 查询脚本

提供命令行和函数接口查询养老金产品数据库。

用法:
    # 按名称模糊搜索（全文搜索）
    python query_pension.py search "平安"
    python query_pension.py search "稳健增值"

    # 按代码精确查找
    python query_pension.py code PAA001.YLJ

    # 按管理人筛选
    python query_pension.py manager PA
    python query_pension.py manager 平安养老

    # 按产品类型筛选
    python query_pension.py type A          # 权益型
    python query_pension.py type C          # 债券型
    python query_pension.py type Cb         # 债券型-信用债子类

    # 统计概览
    python query_pension.py stats

    # 导出全部数据为 CSV
    python query_pension.py export pension_products.csv

    # 组合筛选（管理人 + 类型）
    python query_pension.py filter --manager PA --type A

    # 自定义 SQL 查询
    python query_pension.py sql "SELECT code, name FROM pension_products WHERE name LIKE '%增值%'"
"""

import argparse
import csv
import os
import sqlite3
import sys
from pathlib import Path


def get_db_path(custom_path: str = None) -> str:
    """获取数据库路径。"""
    if custom_path:
        return custom_path
    default = Path(__file__).parent.parent / "data" / "pension_products.db"
    if default.exists():
        return str(default)
    raise FileNotFoundError(
        f"数据库不存在: {default}\n请先运行 build_pension_db.py 构建数据库"
    )


def get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- 查询函数（可被外部 import 使用） ----------

def search(db_path: str, keyword: str, limit: int = 50) -> list[dict]:
    """全文搜索：按名称、代码、管理人等关键词搜索。"""
    conn = get_conn(db_path)
    # 先尝试 FTS5 全文搜索
    try:
        rows = conn.execute("""
            SELECT p.* FROM pension_products p
            JOIN pension_fts f ON p.rowid = f.rowid
            WHERE pension_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (keyword, limit)).fetchall()
        if rows:
            return [dict(r) for r in rows]
    except sqlite3.OperationalError:
        pass

    # 回退到 LIKE 搜索
    like_kw = f"%{keyword}%"
    rows = conn.execute("""
        SELECT * FROM pension_products
        WHERE name LIKE ? OR official_name LIKE ? OR code LIKE ?
           OR manager_name LIKE ? OR product_type_name LIKE ?
        ORDER BY code
        LIMIT ?
    """, (like_kw, like_kw, like_kw, like_kw, like_kw, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_by_code(db_path: str, code: str) -> dict | None:
    """按代码精确查找。"""
    if not code.endswith(".YLJ"):
        code += ".YLJ"
    conn = get_conn(db_path)
    row = conn.execute("SELECT * FROM pension_products WHERE code = ?", (code,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_by_manager(db_path: str, manager: str, limit: int = 200) -> list[dict]:
    """按管理人查询。支持前缀代码或中文名。"""
    conn = get_conn(db_path)
    rows = conn.execute("""
        SELECT * FROM pension_products
        WHERE manager_prefix = ? OR manager_name LIKE ?
        ORDER BY product_type, code
        LIMIT ?
    """, (manager, f"%{manager}%", limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_by_type(db_path: str, ptype: str, limit: int = 500) -> list[dict]:
    """按产品类型查询。ptype: A/B/C/D 或 Ca/Cb/Cf 等子类。"""
    conn = get_conn(db_path)
    if len(ptype) == 1:
        rows = conn.execute("""
            SELECT * FROM pension_products
            WHERE product_type = ?
            ORDER BY manager_prefix, code
            LIMIT ?
        """, (ptype.upper(), limit)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM pension_products
            WHERE bond_subtype = ?
            ORDER BY manager_prefix, code
            LIMIT ?
        """, (ptype, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def filter_products(db_path: str, manager: str = None, ptype: str = None,
                    keyword: str = None, limit: int = 500) -> list[dict]:
    """组合筛选。"""
    conn = get_conn(db_path)
    conditions = []
    params = []

    if manager:
        conditions.append("(manager_prefix = ? OR manager_name LIKE ?)")
        params.extend([manager, f"%{manager}%"])
    if ptype:
        if len(ptype) == 1:
            conditions.append("product_type = ?")
            params.append(ptype.upper())
        else:
            conditions.append("bond_subtype = ?")
            params.append(ptype)
    if keyword:
        conditions.append("(name LIKE ? OR official_name LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    where = " AND ".join(conditions) if conditions else "1=1"
    params.append(limit)

    rows = conn.execute(f"""
        SELECT * FROM pension_products
        WHERE {where}
        ORDER BY manager_prefix, product_type, code
        LIMIT ?
    """, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats(db_path: str) -> dict:
    """获取数据库统计概览。"""
    conn = get_conn(db_path)
    total = conn.execute("SELECT COUNT(*) FROM pension_products").fetchone()[0]

    type_stats = conn.execute("""
        SELECT product_type, product_type_name, COUNT(*) as cnt
        FROM pension_products
        GROUP BY product_type
        ORDER BY cnt DESC
    """).fetchall()

    manager_stats = conn.execute("""
        SELECT manager_prefix, manager_name, COUNT(*) as cnt
        FROM pension_products
        GROUP BY manager_prefix
        ORDER BY cnt DESC
    """).fetchall()

    bond_stats = conn.execute("""
        SELECT bond_subtype, bond_subtype_name, COUNT(*) as cnt
        FROM pension_products
        WHERE bond_subtype IS NOT NULL
        GROUP BY bond_subtype
        ORDER BY cnt DESC
    """).fetchall()

    last_updated = conn.execute(
        "SELECT MAX(last_updated) FROM pension_products"
    ).fetchone()[0]

    conn.close()
    return {
        "total": total,
        "last_updated": last_updated,
        "by_type": [dict(r) for r in type_stats],
        "by_manager": [dict(r) for r in manager_stats],
        "by_bond_subtype": [dict(r) for r in bond_stats],
    }


def export_csv(db_path: str, output_path: str):
    """导出全部数据为 CSV。"""
    conn = get_conn(db_path)
    rows = conn.execute("SELECT * FROM pension_products ORDER BY code").fetchall()
    conn.close()

    if not rows:
        print("数据库为空")
        return

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))
    print(f"已导出 {len(rows)} 条记录到 {output_path}")


def run_sql(db_path: str, query: str, limit: int = 100) -> list[dict]:
    """执行自定义 SQL 查询。"""
    conn = get_conn(db_path)
    rows = conn.execute(query).fetchall()[:limit]
    conn.close()
    return [dict(r) for r in rows]


# ---------- 格式化输出 ----------

def print_products(products: list[dict], verbose: bool = False):
    """格式化打印产品列表。"""
    if not products:
        print("未找到匹配的产品")
        return

    print(f"\n共 {len(products)} 个产品:")
    print(f"{'代码':<18} {'名称':<30} {'管理人':<14} {'类型':<10} {'成立日':<12}")
    print("-" * 84)
    for p in products:
        name = (p.get("name") or p.get("official_name") or "")[:28]
        mgr = (p.get("manager_name") or p.get("manager_prefix") or "")[:12]
        ptype = p.get("product_type_name", "")
        if p.get("bond_subtype"):
            ptype = f"{ptype}({p['bond_subtype']})"
        est = p.get("establishment_date") or ""
        print(f"{p['code']:<18} {name:<30} {mgr:<14} {ptype:<10} {est:<12}")

    if verbose and products:
        print(f"\n详细信息 (第一条):")
        for k, v in products[0].items():
            if v is not None:
                print(f"  {k}: {v}")


def print_stats(stats: dict):
    """格式化打印统计信息。"""
    print(f"\n养老金产品数据库概览")
    print(f"{'=' * 50}")
    print(f"总产品数: {stats['total']}")
    print(f"最后更新: {stats['last_updated']}")

    print(f"\n按产品类型:")
    for t in stats["by_type"]:
        print(f"  {t['product_type_name']} ({t['product_type']}): {t['cnt']} 个")

    print(f"\n按管理人:")
    for m in stats["by_manager"]:
        print(f"  {m['manager_name']} ({m['manager_prefix']}): {m['cnt']} 个")

    if stats["by_bond_subtype"]:
        print(f"\n债券型子类分布:")
        for b in stats["by_bond_subtype"]:
            name = b["bond_subtype_name"] or b["bond_subtype"]
            print(f"  {b['bond_subtype']} ({name}): {b['cnt']} 个")


# ---------- CLI ----------

def main():
    parser = argparse.ArgumentParser(description="养老金产品数据库查询工具")
    parser.add_argument("--db", default=None, help="数据库路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")

    sub = parser.add_subparsers(dest="command", help="查询命令")

    # search
    p_search = sub.add_parser("search", help="全文搜索")
    p_search.add_argument("keyword", help="搜索关键词")
    p_search.add_argument("-n", "--limit", type=int, default=50)

    # code
    p_code = sub.add_parser("code", help="按代码查找")
    p_code.add_argument("code", help="产品代码 (如 PAA001.YLJ)")

    # manager
    p_mgr = sub.add_parser("manager", help="按管理人筛选")
    p_mgr.add_argument("manager", help="管理人前缀或名称")

    # type
    p_type = sub.add_parser("type", help="按产品类型筛选")
    p_type.add_argument("ptype", help="类型: A/B/C/D 或子类 Ca/Cb/Cf...")

    # filter
    p_filter = sub.add_parser("filter", help="组合筛选")
    p_filter.add_argument("--manager", "-m", help="管理人")
    p_filter.add_argument("--type", "-t", dest="ptype", help="类型")
    p_filter.add_argument("--keyword", "-k", help="名称关键词")

    # stats
    sub.add_parser("stats", help="统计概览")

    # export
    p_export = sub.add_parser("export", help="导出 CSV")
    p_export.add_argument("output", help="输出文件路径")

    # sql
    p_sql = sub.add_parser("sql", help="自定义 SQL 查询")
    p_sql.add_argument("query", help="SQL 语句")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        db_path = get_db_path(args.db)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    if args.command == "search":
        results = search(db_path, args.keyword, args.limit)
        print_products(results, args.verbose)

    elif args.command == "code":
        result = get_by_code(db_path, args.code)
        if result:
            print_products([result], verbose=True)
        else:
            print(f"未找到产品: {args.code}")

    elif args.command == "manager":
        results = get_by_manager(db_path, args.manager)
        print_products(results, args.verbose)

    elif args.command == "type":
        results = get_by_type(db_path, args.ptype)
        print_products(results, args.verbose)

    elif args.command == "filter":
        results = filter_products(db_path, args.manager, args.ptype, args.keyword)
        print_products(results, args.verbose)

    elif args.command == "stats":
        stats = get_stats(db_path)
        print_stats(stats)

    elif args.command == "export":
        export_csv(db_path, args.output)

    elif args.command == "sql":
        results = run_sql(db_path, args.query)
        if results:
            # 简单表格输出
            keys = list(results[0].keys())
            print("\t".join(keys))
            for r in results:
                print("\t".join(str(r.get(k, "")) for k in keys))
            print(f"\n共 {len(results)} 条结果")
        else:
            print("无结果")


if __name__ == "__main__":
    main()
