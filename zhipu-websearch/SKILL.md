---
name: zhipu-websearch
description: |
  智谱AI (Z.AI) Web Search API 联网搜索技能。当需要搜索互联网获取实时信息、新闻、
  技术文档、行业动态等内容时使用。支持两种搜索引擎、时间范围过滤、域名过滤等。
  触发词: "搜索", "联网搜索", "web search", "查一下", "最新消息", "搜一下",
  "帮我查", "网上搜", "zhipu search", "智谱搜索"
allowed-tools: Bash Read Glob Grep WebFetch AskUserQuestion
user-invokable: true
---

# 智谱AI Web Search — 联网搜索技能

通过智谱AI的 Web Search API 搜索互联网，获取实时、最新的网页结果。

## Configuration

**Base URL:** `https://api.z.ai/api/paas/v4/web_search`

**Auth:** Bearer Token，格式 `Authorization: Bearer <api_key>`

### API Key 解析（首次调用前必须执行）

```bash
ZHIPU_API_KEY=""

# 1. 环境变量
ZHIPU_API_KEY="${ZHIPU_API_KEY:-${ZHIPU_WEBSEARCH_KEY:-}}"

# 2. 当前目录 key.txt
if [ -z "$ZHIPU_API_KEY" ] && [ -f key.txt ]; then
  ZHIPU_API_KEY=$(cat key.txt | tr -d '[:space:]')
fi

# 3. .env 文件
if [ -z "$ZHIPU_API_KEY" ] && [ -f .env ]; then
  ZHIPU_API_KEY=$(grep -E '^ZHIPU_API_KEY=' .env | cut -d= -f2- | tr -d '"'"'"' ')
fi
if [ -z "$ZHIPU_API_KEY" ] && [ -f ~/.env ]; then
  ZHIPU_API_KEY=$(grep -E '^ZHIPU_API_KEY=' ~/.env | cut -d= -f2- | tr -d '"'"'"' ')
fi
```

**如果 `$ZHIPU_API_KEY` 仍为空**，使用 `AskUserQuestion` 询问用户提供 API Key。

## 搜索引擎选择

| 引擎 | `search_engine` 值 | 特点 | 推荐场景 |
|------|-------------------|------|---------|
| 智谱Premium | `search-prime` | 默认引擎，中文搜索质量高，返回10条结果 | 中文搜索、通用搜索 |
| Jina Pro | `search_pro_jina` | 支持 count/域名过滤/时间过滤，最多50条 | 需要精确过滤、英文搜索、批量结果 |

**选择逻辑：**
1. 中文通用搜索 → `search-prime`（默认，质量最优）
2. 需要控制结果数量（>10条）→ `search_pro_jina`
3. 需要域名过滤 → `search_pro_jina`
4. 需要时间过滤 → 两者都支持，但 `search_pro_jina` 更可靠

## API 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `search_engine` | string | 是 | `search-prime` | 搜索引擎：`search-prime` 或 `search_pro_jina` |
| `search_query` | string | 是 | — | 搜索关键词 |
| `count` | int | 否 | 10 | 返回结果数，1-50（仅 `search_pro_jina`） |
| `search_domain_filter` | string | 否 | — | 限定域名，如 `arxiv.org`（仅 `search_pro_jina`） |
| `search_recency_filter` | string | 否 | `noLimit` | 时间范围过滤（仅 `search_pro_jina`） |
| `request_id` | string | 否 | 自动生成 | 请求唯一标识 |
| `user_id` | string | 否 | — | 终端用户ID |

### 时间过滤选项 (`search_recency_filter`)

| 值 | 含义 |
|----|------|
| `oneDay` | 最近一天 |
| `oneWeek` | 最近一周 |
| `oneMonth` | 最近一月 |
| `oneYear` | 最近一年 |
| `noLimit` | 不限（默认） |

## 搜索调用模板

### 基础搜索（search-prime，推荐）

```bash
curl -s -X POST "https://api.z.ai/api/paas/v4/web_search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ZHIPU_API_KEY" \
  -d '{
    "search_engine": "search-prime",
    "search_query": "搜索关键词"
  }'
```

### 高级搜索（search_pro_jina，支持过滤）

```bash
curl -s -X POST "https://api.z.ai/api/paas/v4/web_search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ZHIPU_API_KEY" \
  -d '{
    "search_engine": "search_pro_jina",
    "search_query": "搜索关键词",
    "count": 10,
    "search_recency_filter": "oneWeek",
    "search_domain_filter": "example.com"
  }'
```

## 响应格式

```json
{
  "id": "请求ID",
  "created": 1773626155,
  "search_intent": [
    {
      "intent": "SEARCH_ALWAYS",
      "keywords": "优化后的关键词",
      "query": "原始查询"
    }
  ],
  "search_result": [
    {
      "title": "网页标题",
      "content": "内容摘要",
      "link": "网页URL",
      "media": "网站名称",
      "icon": "网站图标URL",
      "refer": "ref_1",
      "publish_date": "发布日期"
    }
  ]
}
```

## 工作流模式

### Pattern A: 快速搜索

用户问一个需要联网信息的问题 → 按上述步骤解析 Key → 执行搜索 → 综合结果回答并附上来源链接。

```bash
RESULT=$(curl -s -X POST "https://api.z.ai/api/paas/v4/web_search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ZHIPU_API_KEY" \
  -d '{
    "search_engine": "search-prime",
    "search_query": "用户的搜索问题"
  }')

echo "$RESULT" | python3 -m json.tool
```

### Pattern B: 多轮深入搜索

复杂问题需要多次搜索时：
1. 第一次搜索获取概况
2. 根据结果提炼更精确的关键词
3. 第二次搜索获取细节
4. 综合所有结果给出完整答案

### Pattern C: 定向搜索（限定来源）

需要特定来源的信息：

```bash
# 只搜索 GitHub 上的结果
curl -s -X POST "https://api.z.ai/api/paas/v4/web_search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ZHIPU_API_KEY" \
  -d '{
    "search_engine": "search_pro_jina",
    "search_query": "关键词",
    "search_domain_filter": "github.com",
    "count": 20
  }'
```

### Pattern D: 时效性搜索

需要最新信息：

```bash
# 只搜索最近一天的结果
curl -s -X POST "https://api.z.ai/api/paas/v4/web_search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ZHIPU_API_KEY" \
  -d '{
    "search_engine": "search_pro_jina",
    "search_query": "关键词",
    "search_recency_filter": "oneDay",
    "count": 15
  }'
```

## 结果呈现格式

搜索结果应以简洁方式呈现给用户：

**正文引用：** `相关内容描述 [[1]](url)`

**末尾来源列表：**
```
## 来源
1. [标题](url) — 摘要
2. [标题](url) — 摘要
```

## 错误处理

| HTTP 状态 | 含义 | 处理 |
|-----------|------|------|
| 200 | 成功 | 正常解析 |
| 401 | 认证失败 | 检查 API Key 是否正确 |
| 429 | 频率限制 | 等待几秒后重试 |
| 500 | 服务器错误 | 重试一次，仍失败则告知用户 |

## 注意事项

- `search-prime` 是默认首选引擎，中文搜索质量最佳
- `search_pro_jina` 适合需要精确过滤的场景
- 搜索关键词应简洁精准，避免过长的句子
- 中文搜索时用中文关键词，英文内容用英文关键词
- 每次搜索返回结果后，应综合多条结果回答，而非只用一条
- 务必在回答中引用来源链接，增强可信度
