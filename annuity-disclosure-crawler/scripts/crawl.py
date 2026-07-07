#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业年金投资管理人 · 官网季度管理报告 全量爬取驱动
=================================================
读取 references/registry.json，按每家机构的 strategy 抓取官网披露栏目下
**全部历史季度**的《企业年金基金投资管理情况》报告，落地到 --out 目录，
并做真伪校验(魔数/大小)与清单(manifest)记录。

纯 HTTP 可搞定的策略：pdf_index / detail_index / html_index / spa_api(部分)
需浏览器的策略：headless（本脚本跳过并提示改用 crawl_headless.py）
不公开：login_blocked（跳过并说明）

用法:
  python3 crawl.py --list                      # 只列出名录与每家策略/入口
  python3 crawl.py                             # 全量抓取所有可 HTTP 抓取的机构
  python3 crawl.py --only m04,m09,m17          # 只抓指定机构(逗号分隔 slug 或简称)
  python3 crawl.py --latest 3                  # 每家只保留最新 N 期(默认0=全量)
  python3 crawl.py --out /path/to/out          # 指定输出目录(默认 ./annuity_reports)
  python3 crawl.py --max-pages 40              # 列表分页最多翻多少页(默认30)
  python3 crawl.py --include-waf               # 也尝试对 waf 机构做HTTP直取(多半失败,仅留痕)

依赖: requests  (pip install requests --break-system-packages)
"""
import argparse, json, os, re, sys, time, hashlib
from urllib.parse import urljoin, urlparse, unquote

try:
    import requests
except ImportError:
    sys.exit("需要 requests: pip install requests --break-system-packages")

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = os.path.join(os.path.dirname(HERE), "references", "registry.json")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# 期次识别: 2026Q1 / 2026年1季度 / 2026年第一季度 / 2026-1季度
CN_NUM = {"一": "1", "二": "2", "三": "3", "四": "4"}
PERIOD_RES = [
    re.compile(r"(20\d{2})\s*[Qq]\s*([1-4])"),
    re.compile(r"(20\d{2})\D{0,4}?第?\s*([1-4一二三四])\s*季度"),
]


# 报告标题判别词（区分季报条目 vs 栏目里的其它通知）
TITLE_KW = re.compile(r"管理情况|投资管理|年金.{0,6}报告")


def parse_period(*texts):
    for t in texts:
        if not t:
            continue
        t = unquote(t)
        for rx in PERIOD_RES:
            m = rx.search(t)
            if m:
                q = CN_NUM.get(m.group(2), m.group(2))
                return f"{m.group(1)}Q{q}"
        # 年度报告
        m = re.search(r"(20\d{2})\s*年度", t)
        if m:
            return f"{m.group(1)}A"
    return None


def fetch(url, referer=None, binary=False, timeout=60, session=None):
    s = session or requests
    h = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"}
    if referer:
        h["Referer"] = referer
    r = s.get(url, headers=h, timeout=timeout, allow_redirects=True, verify=False)
    r.raise_for_status()
    if binary:
        return r.content, r.headers.get("Content-Type", "")
    # 文本：尝试正确解码(GBK 站点很多)
    raw = r.content
    ct = r.headers.get("Content-Type", "").lower()
    enc = None
    m = re.search(r"charset=([\w-]+)", ct)
    if m:
        enc = m.group(1)
    if not enc:
        head = raw[:2000].decode("ascii", "ignore").lower()
        m = re.search(r'charset=["\']?([\w-]+)', head)
        if m:
            enc = m.group(1)
    for e in ([enc] if enc else []) + ["utf-8", "gb18030"]:
        try:
            return raw.decode(e), r.headers.get("Content-Type", "")
        except Exception:
            continue
    return raw.decode("utf-8", "ignore"), r.headers.get("Content-Type", "")


def abs_links(html, base):
    """返回 [(href_abs, anchor_text)]"""
    out = []
    for m in re.finditer(r'<a\b[^>]*?href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.I | re.S):
        href = m.group(1).strip()
        if href.startswith(("javascript:", "#", "mailto:")):
            continue
        text = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        out.append((urljoin(base, href), text))
    return out


def file_from_href(href, base, rx):
    """判断一个链接是否指向报告文件，返回可下载的绝对 URL 或 None。
    处理 pdfjs 包装(viewer.html?file=xxx.pdf)、相对路径、以及 .pdf/.docx 后缀兜底。"""
    cands = [href]
    m = re.search(r"[?&]file=([^&]+)", href)
    if m:
        cands.append(unquote(m.group(1)))
    for c in cands:
        cabs = urljoin(base, c)
        if rx and (rx.search(c) or rx.search(cabs)):
            return cabs
        if c.split("?")[0].lower().endswith((".pdf", ".docx", ".doc", ".xlsx")):
            return cabs
    return None


def files_in_page(html, base, rx):
    """从一个页面里挖出所有报告文件直链（详情页二跳用）。"""
    hits = set()
    for href, _ in abs_links(html, base):
        f = file_from_href(href, base, rx)
        if f:
            hits.add(f)
    if rx:
        for m in rx.finditer(html):
            hits.add(urljoin(base, m.group(0)))
    # 裸露的 .pdf/.docx 直链(在 JS/iframe src 里)——必须是真路径(以 / 或 http 开头)，
    # 避免把详情页里的“显示用中文文件名”误当成同目录相对链接
    for m in re.finditer(r'["\']((?:https?:)?/[^"\'\s]+\.(?:pdf|docx))["\']', html, re.I):
        hits.add(urljoin(base, m.group(1)))
    return list(hits)


def list_pages(mgr, max_pages):
    """生成要翻的列表页 URL（去重、保序）。
    很多站点第 1 页是 index.html（无编号），第 2 页起才是 index_1/index2…，
    因此始终把 disclosure_url 作为首页，再拼编号页。"""
    lu = mgr.get("list_url")
    disc = mgr.get("disclosure_url")
    if not lu:
        return [disc] if disc else []
    if "{n}" not in lu:
        return [lu]
    known = mgr.get("list_pages_known")
    top = known if known else max_pages
    seq = [disc] + [lu.replace("{n}", str(i)) for i in range(1, top + 1)]
    seen, out = set(), []
    for u in seq:
        if u and u not in seen:
            seen.add(u); out.append(u)
    return out


def verify(path, item_type):
    try:
        sz = os.path.getsize(path)
    except OSError:
        return False, 0, "missing"
    if sz < 512:
        return False, sz, "too-small"
    with open(path, "rb") as f:
        head = f.read(8)
    if item_type == "pdf":
        return (head[:4] == b"%PDF", sz, "ok" if head[:4] == b"%PDF" else "not-pdf")
    if item_type == "docx":
        return (head[:2] == b"PK", sz, "ok" if head[:2] == b"PK" else "not-docx")
    # html
    with open(path, "rb") as f:
        body = f.read(60000)
    txt = body.decode("utf-8", "ignore") + body.decode("gb18030", "ignore")
    ok = ("年金" in txt or "<title" in txt.lower()) and b"<html" in body.lower() or sz > 3000
    return (bool(ok), sz, "ok" if ok else "suspect")


def safe_name(period, url, item_type, slug):
    ext = {"pdf": ".pdf", "docx": ".docx", "html": ".html"}[item_type]
    base = period or ("item_" + hashlib.md5(url.encode()).hexdigest()[:8])
    return f"{slug}_{base}{ext}"


def crawl_manager(mgr, outdir, latest, max_pages, include_waf):
    slug = mgr["slug"]
    strat = mgr["strategy"]
    item_type = mgr["item_type"]
    res = {"slug": slug, "name": mgr["name"], "strategy": strat, "access": mgr["access"],
           "disclosure_url": mgr["disclosure_url"], "files": [], "skipped": None}

    if strat == "login_blocked":
        res["skipped"] = "login/非公开：季报仅登录客户门户可见或未在官网公开"
        return res
    if strat in ("headless",) and not include_waf:
        res["skipped"] = "需无头浏览器(WAF/SPA)：改用 crawl_headless.py 或加 --include-waf 试探"
        return res

    d = os.path.join(outdir, slug)
    os.makedirs(d, exist_ok=True)
    sess = requests.Session()
    pat = mgr.get("file_url_pattern")
    rx = re.compile(pat) if pat else None

    # 1) 逐列表页收集候选（锚点为主，带标题文本→可解析期次并过滤非报告条目）
    found = {}          # file_url -> period   (pdf_index/html_index 的最终文件)
    detail_q = {}       # detail_url -> period (detail_index 需二跳)
    pages = list_pages(mgr, max_pages) or [mgr["disclosure_url"]]
    empty_streak = 0
    for i, pg in enumerate(pages):
        try:
            html, _ = fetch(pg, referer=mgr["disclosure_url"], session=sess)
        except Exception:
            empty_streak += 1
            if empty_streak >= 2:
                break
            continue
        if i == 0:
            with open(os.path.join(d, "_disclosure_page.html"), "w", encoding="utf-8", errors="ignore") as f:
                f.write(html)
        new = 0
        for href, text in abs_links(html, pg):
            p = parse_period(text, href)
            titled = bool(text and TITLE_KW.search(text))
            if not (p or titled):
                continue                      # 不像报告条目，跳过（滤掉栏目里的其它通知/导航）
            direct = file_from_href(href, pg, rx)
            if direct:                        # 锚点本身就是文件(或 pdfjs 包装) → 直接收
                if direct not in found:
                    found[direct] = p; new += 1
            elif rx and rx.search(href):      # 锚点是 html 报告页(html_index) → 收
                if href not in found:
                    found[href] = p; new += 1
            elif strat in ("detail_index", "spa_api"):   # 是详情页 → 二跳
                if href not in detail_q:
                    detail_q[href] = (p, text); new += 1
        # pdf_index 兜底：直链可能不在 <a> 里（onclick 等），用正则再捞一遍（要求文件名自带期次）
        if strat == "pdf_index" and rx:
            for m in rx.finditer(html):
                u = urljoin(pg, m.group(0))
                pu = parse_period(u)
                if pu and u not in found:
                    found[u] = pu; new += 1
        empty_streak = 0 if new else empty_streak + 1
        if empty_streak >= 3:
            break
        time.sleep(0.3)

    # 2) detail_index：进详情页取文件直链
    for href, (p, text) in detail_q.items():
        try:
            html, _ = fetch(href, referer=mgr["disclosure_url"], session=sess)
        except Exception:
            continue
        for u in files_in_page(html, href, rx):
            if u not in found:
                found[u] = parse_period(u) or p
        time.sleep(0.2)

    if not found:
        res["skipped"] = "HTTP 抓取 0 命中：列表多为 JS 渲染或被拦，请改用 crawl_headless.py"
        return res

    # 3) 排序、按 latest 截断（保留最新 N 个不同期次的全部报告）、下载
    items = sorted(found.items(), key=lambda kv: (kv[1] or ""), reverse=True)
    if latest and latest > 0:
        periods_kept, kept = [], []
        for u, p in items:
            if p is None:
                continue                      # 无法定期次的条目在 latest 模式下略过
            if p not in periods_kept:
                if len(periods_kept) >= latest:
                    break
                periods_kept.append(p)
            kept.append((u, p))
        items = kept

    seen_md5 = set()
    for u, period in items:
        try:
            content, ct = fetch(u, referer=mgr["disclosure_url"], binary=True, session=sess)
        except Exception as e:
            res["files"].append({"url": u, "period": period, "status": f"download-fail:{e}", "local": None, "bytes": 0})
            continue
        h = hashlib.md5(content).hexdigest()
        if h in seen_md5:
            continue                        # 同一报告被多个 URL 变体重复收录，按内容去重
        seen_md5.add(h)
        # 若声明 pdf 却拿到 html 错误页
        it = item_type
        if item_type == "pdf" and content[:4] != b"%PDF" and content[:2] == b"PK":
            it = "docx"
        name = safe_name(period, u, it, slug)
        path = os.path.join(d, name)
        if os.path.exists(path):    # 同期两类报告(投资管理/集合计划)等→加短哈希防覆盖
            stem, ext = os.path.splitext(name)
            path = os.path.join(d, f"{stem}_{hashlib.md5(u.encode()).hexdigest()[:6]}{ext}")
        with open(path, "wb") as f:
            f.write(content)
        ok, sz, why = verify(path, it)
        if not ok:
            os.rename(path, path + ".suspect")
            path = path + ".suspect"
        res["files"].append({"url": u, "period": period, "status": why,
                             "local": os.path.relpath(path), "bytes": sz})
        time.sleep(0.2)
    return res


def main():
    import urllib3
    urllib3.disable_warnings()
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default=REGISTRY)
    ap.add_argument("--out", default="annuity_reports")
    ap.add_argument("--only", default="")
    ap.add_argument("--latest", type=int, default=0, help="每家保留最新N期，0=全量")
    ap.add_argument("--max-pages", type=int, default=30)
    ap.add_argument("--include-waf", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    reg = json.load(open(args.registry, encoding="utf-8"))
    managers = reg["managers"]

    if args.list:
        print(f"{'slug':5} {'简称':10} {'access':7} {'strategy':13} 披露入口")
        for m in managers:
            print(f"{m['slug']:5} {m['short']:10} {m['access']:7} {m['strategy']:13} {m['disclosure_url']}")
        return

    only = [x.strip() for x in args.only.split(",") if x.strip()]
    if only:
        managers = [m for m in managers if m["slug"] in only or m["short"] in only]

    os.makedirs(args.out, exist_ok=True)
    all_res = []
    for m in managers:
        print(f"\n=== {m['slug']} {m['short']} [{m['strategy']}/{m['access']}] ===", flush=True)
        r = crawl_manager(m, args.out, args.latest, args.max_pages, args.include_waf)
        if r["skipped"]:
            print("  ⏭  " + r["skipped"])
        else:
            okn = sum(1 for f in r["files"] if f["status"] == "ok")
            print(f"  ✓ {okn}/{len(r['files'])} 个文件有效，落地 {os.path.join(args.out, m['slug'])}/")
            for f in r["files"][:6]:
                print(f"     [{f['period']}] {f['status']} {f['bytes']}B  {f['local']}")
        all_res.append(r)

    # manifest
    mani = os.path.join(args.out, "manifest.json")
    json.dump({"generated": time.strftime("%Y-%m-%d %H:%M"), "results": all_res},
              open(mani, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    import csv
    with open(os.path.join(args.out, "manifest.csv"), "w", newline="", encoding="utf-8-sig") as fp:
        w = csv.writer(fp)
        w.writerow(["slug", "机构", "策略", "access", "期次", "状态", "字节", "本地路径", "源URL"])
        for r in all_res:
            if r["skipped"]:
                w.writerow([r["slug"], r["name"], r["strategy"], r["access"], "", "SKIP:" + r["skipped"], "", "", ""])
            for f in r["files"]:
                w.writerow([r["slug"], r["name"], r["strategy"], r["access"], f["period"], f["status"], f["bytes"], f["local"], f["url"]])
    tot = sum(len(r["files"]) for r in all_res)
    okt = sum(1 for r in all_res for f in r["files"] if f["status"] == "ok")
    print(f"\n完成：{okt}/{tot} 个有效文件。清单：{mani} 及 manifest.csv")


if __name__ == "__main__":
    main()
