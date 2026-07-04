#!/usr/bin/env python3
"""
agentrs-search —— 京东 agentrs 代理网关的「联网搜索」客户端。

封装 4 个搜索引擎：tavily / cloudsway(Bing) / SearchPro(搜狗) / jdcloud_search(京东云RAG)。
端点：https://agentrs.jd.com/api/saas/proxy-k/v1/<tool>

鉴权：环境变量 JD_AGENTRS_TOKEN（不硬编码密钥）。
  export JD_AGENTRS_TOKEN='...'

约定：网关一律从 JSON body 取参（query string 不生效）；HTTP 恒 200，业务看 body。
  1001=工具未授权 | 9999"缺少必要输入参数"=参数错 | 9999"积分不足"=余额不足(可重试)。

用法：
  python3 search.py tavily    "人工智能最新趋势"
  python3 search.py cloudsway "中信建投证券" --count 5 --enableContent true --mainText true
  python3 search.py searchpro "今天北京天气"
  python3 search.py jdcloud   "AI agent 发展"
"""
import os, sys, json, argparse, urllib.request, urllib.error

BASE = "https://agentrs.jd.com/api/saas/proxy-k/v1"


def _token():
    tok = os.environ.get("JD_AGENTRS_TOKEN")
    if not tok:
        sys.exit("错误：未设置 JD_AGENTRS_TOKEN。\n  export JD_AGENTRS_TOKEN='你的token'")
    return tok


def call(tool, body, timeout=30):
    payload = {k: v for k, v in body.items() if v not in ("", None)}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/{tool}", data=data, method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {_token()}"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8")
    except urllib.error.URLError as e:
        return {"_error": f"网络错误: {e}"}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw": raw}


def biz_error(resp):
    if not isinstance(resp, dict):
        return None
    code, msg = resp.get("code"), resp.get("msg") or ""
    if code in (1001, "1001"):
        return f"[未授权 1001] 该 token 未开通此工具：{msg}"
    if code in (9999, "9999") or "积分不足" in msg or "缺少必要输入参数" in msg:
        return f"[业务失败 {code}] {msg}"
    return None


# 4 个搜索引擎 -------------------------------------------------
def tavily(query, **k):
    return call("tavily_search", {"query": query})

def cloudsway(q, count="", freshness="", offset="", enableContent="",
              contentType="", mainText="", sites="", blockWebsites="", **k):
    return call("cloudsway", dict(q=q, count=count, freshness=freshness, offset=offset,
                enableContent=enableContent, contentType=contentType, mainText=mainText,
                sites=sites, blockWebsites=blockWebsites))

def searchpro(query, region="", mode="", site="", cnt="", industry="", **k):
    return call("SearchPro", dict(Query=query, Region=region, Mode=mode,
                site=site, Cnt=cnt, Industry=industry))

def jdcloud(query, **k):
    return call("jdcloud_search", {"query": query})


TOOLS = {"tavily": tavily, "cloudsway": cloudsway,
         "searchpro": searchpro, "jdcloud": jdcloud}


def main():
    p = argparse.ArgumentParser(description="京东 agentrs 联网搜索（4 引擎）")
    p.add_argument("engine", choices=list(TOOLS))
    p.add_argument("query", nargs="?", help="查询词")
    for opt in ("count", "freshness", "offset", "enableContent", "contentType",
                "mainText", "sites", "blockWebsites", "region", "mode",
                "site", "cnt", "industry"):
        p.add_argument(f"--{opt}", default=None)
    a = p.parse_args()
    kw = {k: v for k, v in vars(a).items()
          if k not in ("engine", "query") and v is not None}
    if a.query:
        kw["q" if a.engine == "cloudsway" else "query"] = a.query
    resp = TOOLS[a.engine](**kw)
    err = biz_error(resp)
    if err:
        print(err, file=sys.stderr)
    print(json.dumps(resp, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
