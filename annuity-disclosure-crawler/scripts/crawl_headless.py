#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业年金季报爬取 · 无头浏览器兜底
================================
用于 crawl.py 搞不定的机构：列表页是 SPA(JS 渲染) 或整站有反爬 WAF/JS 挑战
（strategy=headless / spa_api，或 access=waf）。用真实 Chromium 渲染页面、
自动通过瑞数/加速乐等 JS 挑战、取到报告链接后用带 Cookie 的浏览器上下文下载。

依赖:
  pip install playwright --break-system-packages
  python3 -m playwright install chromium

用法:
  python3 crawl_headless.py --only m15,m21        # 指定机构
  python3 crawl_headless.py                        # 默认抓所有 headless/spa_api/waf 机构
  python3 crawl_headless.py --latest 3 --out DIR   # 同 crawl.py 语义
  python3 crawl_headless.py --only m21 --headful   # 显示浏览器窗口(调试/过人机)

与 crawl.py 复用同一 registry.json 与期次识别/校验/命名逻辑。
"""
import argparse, json, os, sys, time, hashlib, re, csv

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import crawl  # 复用 parse_period / file_from_href / files_in_page / verify / safe_name / TITLE_KW / list_pages

from playwright.sync_api import sync_playwright

UA = crawl.UA
REGISTRY = crawl.REGISTRY


def harvest_links(page):
    """返回页面上所有 <a> 的 (href_abs, text)。"""
    return page.eval_on_selector_all(
        "a",
        "els => els.map(a => [a.href, (a.innerText||a.textContent||'').trim()])",
    )


def crawl_manager(ctx, mgr, outdir, latest, max_pages):
    slug = mgr["slug"]
    strat = mgr["strategy"]
    item_type = mgr["item_type"]
    rx = re.compile(mgr["file_url_pattern"]) if mgr.get("file_url_pattern") else None
    res = {"slug": slug, "name": mgr["name"], "strategy": strat, "access": mgr["access"],
           "disclosure_url": mgr["disclosure_url"], "files": [], "skipped": None}
    if strat == "login_blocked":
        res["skipped"] = "登录墙/非公开，浏览器也无法匿名取得"
        return res

    d = os.path.join(outdir, slug)
    os.makedirs(d, exist_ok=True)
    page = ctx.new_page()
    found = {}       # file_url -> period
    detail_q = {}

    pages = crawl.list_pages(mgr, max_pages) or [mgr["disclosure_url"]]
    empty = 0
    for i, pg in enumerate(pages):
        try:
            page.goto(pg, wait_until="networkidle", timeout=45000)
        except Exception:
            try:
                page.goto(pg, wait_until="domcontentloaded", timeout=45000)
            except Exception:
                empty += 1
                if empty >= 2:
                    break
                continue
        time.sleep(2.5)               # 等 JS 挑战/异步渲染
        for _ in range(4):            # 滚动触发懒加载
            page.mouse.wheel(0, 20000)
            time.sleep(0.6)
        if i == 0:
            try:
                open(os.path.join(d, "_disclosure_rendered.html"), "w", encoding="utf-8").write(page.content())
            except Exception:
                pass
        new = 0
        for href, text in harvest_links(page):
            if not href:
                continue
            p = crawl.parse_period(text, href)
            titled = bool(text and crawl.TITLE_KW.search(text))
            if not (p or titled):
                continue
            direct = crawl.file_from_href(href, pg, rx)
            if direct:
                if direct not in found:
                    found[direct] = p; new += 1
            elif strat in ("detail_index", "spa_api", "headless"):
                if href not in detail_q:
                    detail_q[href] = (p, text); new += 1
        empty = 0 if new else empty + 1
        if empty >= 3:
            break

    # 详情页二跳（渲染后取文件链）
    for href, (p, text) in list(detail_q.items()):
        try:
            page.goto(href, wait_until="networkidle", timeout=40000)
            time.sleep(1.5)
        except Exception:
            continue
        html = page.content()
        for u in crawl.files_in_page(html, href, rx):
            if u not in found:
                found[u] = crawl.parse_period(u) or p

    if not found:
        res["skipped"] = "渲染后仍 0 命中：可能需登录、或分页/下载入口需交互(试 --headful 观察)"
        page.close()
        return res

    items = sorted(found.items(), key=lambda kv: (kv[1] or ""), reverse=True)
    if latest and latest > 0:
        periods_kept, kept = [], []
        for u, pp in items:
            if pp is None:
                continue
            if pp not in periods_kept:
                if len(periods_kept) >= latest:
                    break
                periods_kept.append(pp)
            kept.append((u, pp))
        items = kept

    seen_md5 = set()
    for u, period in items:
        try:
            r = ctx.request.get(u, timeout=60000)      # 带浏览器 Cookie 下载，过 WAF
            content = r.body()
        except Exception as e:
            res["files"].append({"url": u, "period": period, "status": f"download-fail:{e}", "local": None, "bytes": 0})
            continue
        h = hashlib.md5(content).hexdigest()
        if h in seen_md5:
            continue
        seen_md5.add(h)
        it = item_type
        if item_type == "pdf" and content[:4] != b"%PDF" and content[:2] == b"PK":
            it = "docx"
        name = crawl.safe_name(period, u, it, slug)
        path = os.path.join(d, name)
        if os.path.exists(path):
            stem, ext = os.path.splitext(name)
            path = os.path.join(d, f"{stem}_{hashlib.md5(u.encode()).hexdigest()[:6]}{ext}")
        open(path, "wb").write(content)
        ok, sz, why = crawl.verify(path, it)
        if not ok:
            os.rename(path, path + ".suspect"); path += ".suspect"
        res["files"].append({"url": u, "period": period, "status": why, "local": os.path.relpath(path), "bytes": sz})
        time.sleep(0.2)
    page.close()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default=REGISTRY)
    ap.add_argument("--out", default="annuity_reports")
    ap.add_argument("--only", default="")
    ap.add_argument("--latest", type=int, default=0)
    ap.add_argument("--max-pages", type=int, default=30)
    ap.add_argument("--headful", action="store_true")
    args = ap.parse_args()

    reg = json.load(open(args.registry, encoding="utf-8"))
    managers = reg["managers"]
    only = [x.strip() for x in args.only.split(",") if x.strip()]
    if only:
        managers = [m for m in managers if m["slug"] in only or m["short"] in only]
    else:  # 默认：需浏览器的那批
        managers = [m for m in managers if m["strategy"] in ("headless", "spa_api") or m["access"] == "waf"]
        managers = [m for m in managers if m["strategy"] != "login_blocked"]

    os.makedirs(args.out, exist_ok=True)
    all_res = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not args.headful)
        ctx = browser.new_context(user_agent=UA, locale="zh-CN", ignore_https_errors=True,
                                  extra_http_headers={"Accept-Language": "zh-CN,zh;q=0.9"})
        for m in managers:
            print(f"\n=== {m['slug']} {m['short']} [{m['strategy']}/{m['access']}] ===", flush=True)
            try:
                r = crawl_manager(ctx, m, args.out, args.latest, args.max_pages)
            except Exception as e:
                r = {"slug": m["slug"], "name": m["name"], "strategy": m["strategy"], "access": m["access"],
                     "disclosure_url": m["disclosure_url"], "files": [], "skipped": f"异常:{e}"}
            if r["skipped"]:
                print("  ⏭  " + r["skipped"])
            else:
                okn = sum(1 for f in r["files"] if f["status"] == "ok")
                print(f"  ✓ {okn}/{len(r['files'])} 个有效，落地 {os.path.join(args.out, m['slug'])}/")
                for f in r["files"][:6]:
                    print(f"     [{f['period']}] {f['status']} {f['bytes']}B  {f['local']}")
            all_res.append(r)
        browser.close()

    mani = os.path.join(args.out, "manifest_headless.json")
    json.dump({"generated": time.strftime("%Y-%m-%d %H:%M"), "results": all_res},
              open(mani, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    with open(os.path.join(args.out, "manifest_headless.csv"), "w", newline="", encoding="utf-8-sig") as fp:
        w = csv.writer(fp)
        w.writerow(["slug", "机构", "策略", "access", "期次", "状态", "字节", "本地路径", "源URL"])
        for r in all_res:
            if r["skipped"]:
                w.writerow([r["slug"], r["name"], r["strategy"], r["access"], "", "SKIP:" + r["skipped"], "", "", ""])
            for f in r["files"]:
                w.writerow([r["slug"], r["name"], r["strategy"], r["access"], f["period"], f["status"], f["bytes"], f["local"], f["url"]])
    okt = sum(1 for r in all_res for f in r["files"] if f["status"] == "ok")
    print(f"\n完成：{okt} 个有效文件。清单：{mani}")


if __name__ == "__main__":
    main()
