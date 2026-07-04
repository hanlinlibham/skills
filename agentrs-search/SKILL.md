---
name: agentrs-search
description: >
  联网搜索工具箱 —— 通过京东 agentrs 代理网关，用单一 Bearer Token 调用 4 个搜索引擎：
  tavily(AI搜索)、cloudsway(必应/Bing,可拿网页全文)、SearchPro(搜狗,实时新闻时效最强)、
  jdcloud_search(京东云RAG,返回整页正文)。当需要联网检索资讯、新闻、研报、实时信息，
  或要抓取网页正文做后续分析时使用。触发词：联网搜索、实时搜索、查资讯、查新闻、
  搜一下、tavily、bing、cloudsway、搜狗、京东搜索、web search、抓网页正文。
---

# agentrs-search —— 联网搜索（4 引擎）

通过 `https://agentrs.jd.com/api/saas/proxy-k/v1/<tool>`，单一 Bearer Token 调 4 个搜索引擎。

## 鉴权与调用约定（先读）
- 环境变量取密钥，**不硬编码**：`export JD_AGENTRS_TOKEN='你的token'`
- **网关只认 JSON body**：文档标 GET/POST 都不影响，query string 会报"缺少必要输入参数"。
- HTTP 恒 200，业务看 body：`1001`=token 未授权（充值/补参无用）；`9999 缺少必要输入参数`=参数错；`9999 用户积分不足`=余额不足（**重试常能通**）。

## 4 个引擎怎么选
| 引擎 | 底层 | 入参 | 结果路径 | 选用场景 |
|---|---|---|---|---|
| `tavily` | Tavily | `{query}` | `results[]` | 通用 AI 搜索，默认首选 |
| `cloudsway` | Bing/必应 | `{q,count,freshness,enableContent,contentType,mainText,sites,blockWebsites}` | `webPages.value[]` | 中文好；`enableContent=true` 直接拿网页**正文**；`sites/blockWebsites` 站点过滤；`freshness=Day/Week/Month` 时间过滤 |
| `searchpro` | 搜狗 | `{Query,Cnt,Site,Industry,...}` | `Response.Pages[]`（**元素是字符串化JSON，需二次 parse**） | **实时新闻/天气，时效性最强** |
| `jdcloud` | 京东云 RAG | `{query}` | `data[]`（`page_content` 整页正文 + `recall_distance`） | 要**整页全文**做分析时 |

## 用法
```bash
export JD_AGENTRS_TOKEN='...'
python3 scripts/search.py tavily    "人工智能最新趋势"
python3 scripts/search.py cloudsway "中信建投证券" --count 5 --enableContent true --mainText true
python3 scripts/search.py searchpro "今天北京天气"
python3 scripts/search.py jdcloud   "AI agent 发展"
```
打印规整 JSON；遇 1001/9999 在 stderr 给可读提示。

## 直接 curl
```bash
curl -s https://agentrs.jd.com/api/saas/proxy-k/v1/tavily_search \
  -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JD_AGENTRS_TOKEN" \
  -d '{"query":"搜索关键词"}'
```
工具名换 `cloudsway`/`SearchPro`/`jdcloud_search`、body 换对应入参即可。

## 选用范式
- 通用检索 → `tavily`；要最新时效 → `searchpro`；要网页正文做分析 → `jdcloud`（或 `cloudsway --enableContent true`）；要限定站点 → `cloudsway --sites baijiahao.baidu.com`。

> 地图/经纬度/POI/路径 等见姊妹 skill **agentrs-map**；天气见 **agentrs-weather**。三者共用同一个 JD_AGENTRS_TOKEN。
