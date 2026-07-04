---
name: ablemind-ops
description: >
  AbleMind 私域平台(portal / skill-market / gitea，部署在 heyun01)运维手册。
  覆盖部署上线流程、一组踩过坑的硬规矩、以及今天确立的架构/安全原则
  (工作区即上线、密钥绝不进浏览器、共享顶栏单一来源、登录闸门、digest 数据解耦、
  token 安全)。还含一套无头浏览器验证技巧。
  当需要部署/上线 ablemind_portal、在 heyun01 上做运维、排查线上回归、
  或评审"key 暴露 / 顶栏不同步 / 页面只读门禁 / digest 看不到"这类问题时使用。
  触发词：部署、上线、运维、deploy、heyun01、ablemind 部署、digest/MCP/Hub 维护、
  线上回归、key 泄露、顶栏不同步、登录闸门。
---

# AbleMind 运维手册（ablemind-ops）

私域平台 monorepo `ablemind_portal` 的运维 playbook。**完整部署细节见仓库根目录 `DEPLOY.md`**；
本 skill 是"怎么想 + 怎么干 + 别再踩的坑"。

## 0. 拓扑速记

| 服务 | 子目录 | heyun01 路径 | 进程 | 端口 | 域名 |
|---|---|---|---|---|---|
| portal | `portal/` | `/opt/portal` | systemd `portal.service` | 8103 | `ablemind.cc` |
| skill-market | `skill-market/web/` | `/opt/skill-market/web` | systemd `skill-market.service` | 8102 | `skill.ablemind.cc` |
| gitea | `gitea/` | `/opt/gitea` | docker `gitea` | 3001 | `git.ablemind.cc` |

- nginx 反代 + `*.ablemind.cc` 通配证书 + Casdoor SSO(`cas.itseek.cc`)；Node v22。
- **heyun01 = tailnet 节点 `ser1554776700`(`100.113.172.75`)，root。** 本机若无 `heyun01` ssh 别名：
  `DEPLOY_HOST="root@100.113.172.75" ./deploy.sh <target>`。

## 1. 部署流程

```bash
DEPLOY_HOST="root@100.113.172.75" ./deploy.sh portal|skill-market|gitea|all
```
每个目标 = rsync 源码 → 远端 `npm install && npm run build && systemctl restart` →打印 `is-active`。
gitea 是 `docker compose up -d && restart`（重载顶栏模板）。结尾 `✔ done`。

**部署前三连查**（顺序别省）：
1. `git status` —— **deploy 同步的是工作区，不是 git HEAD**。任何未提交改动(包括别的会话的 WIP)都会被一起 rsync 上线。这是共享工作区，务必确认要上线的就是你以为的那份。
2. `git log origin/main..HEAD` / `HEAD..origin/main` —— 与远程对齐。
3. 本地 `npm run build` 过 + **确认相关 env 已在 host**（见 §3）。改了什么就只部署什么。

## 2. 必须记住的坑（都真实踩过）

- **`src/` 之外、运行时要读的文件，必须在 `deploy.sh` 里显式同步**，否则 build 能过、运行时空/404：
  - `portal/public/`（共享顶栏 `topbar.js` + 品牌 `ablm-logo.png`）—— rsync **不带 `--delete`**(曾误删 logo)。
  - `skill-market/web/config/`（`mcp.json` + `mcp-introspect.json`，`/data` 运行时读 `cwd/config`）。
  - `gitea/templates/custom/body_outer_pre.tmpl`（顶栏静态模板）+ 容器 restart。
- **rsync 排除 `/data` 必须带前导斜杠锚定**：无锚的 `data` 会误伤 `src/app/data`、`src/components/data` 等源码目录(踩过 /data 路由 404)。
- **`.env` 永不覆盖**(rsync 排除)；密钥只在 host。改 prod `.env` 属敏感操作，**让用户授权/自己跑**，别擅自写。
- **共享顶栏改了要升版本号**：`topbar.js` 被 Cloudflare 缓存约 4h。改它后必须在三处把 `?v=N` 升一位
  (`portal/src/app/layout.tsx`、`skill-market/web/src/app/layout.tsx`、`gitea/.../body_outer_pre.tmpl`)，否则新菜单不生效。
- **heyun01 上别热改源码** —— 下次 rsync 覆盖。
- **nginx 代理缓冲必须 ≥32k**(已配,在 /etc/nginx/sites-enabled/ 两个 vhost):auth 回调一次下发
  多个大 Set-Cookie(会话 JWT + Casdoor id_token),默认 4k 会报 `upstream sent too big header` → 502。
  用户侧表象是 Cloudflare 502 错误页(链路图 Host=Error),别误判成 Tunnel/Cloudflare 故障 —— 先查
  heyun01 的 /var/log/nginx/error.log 对时间戳。

## 2.5 ablework / dpagt 研究后端（ali-lab，独立机，非 heyun01）

研究舰队后端不在 heyun01，而在 **ali-lab**（ssh 别名 `ali-lab` = `39.96.218.64` = `ab.itseek.cc`，root）。

| 项 | 值 |
|---|---|
| 进程 | pm2 `backend`（`infisical run -- python server.py`，wrapper `deploy/backend-infisical-wrapper.sh`） |
| 路径 | `/opt/ablemind/able-dpagt/dpagt/backend_dp`，conda env `dpagt_co` |
| 监听 | `127.0.0.1:8202`（nginx `ab.itseek.cc` 反代 `/api`→8202） |
| 调用链 | `skill.ablemind.cc/api/ablework/mcp`(heyun01 skill-market 代理) → 注入用户 Casdoor JWT → 转发 `ab.itseek.cc/api/mcp`(ali-lab:8202) |
| 重启/查日志 | `ssh ali-lab 'pm2 restart backend'`；日志 `tmp/logs/server-{out,error}.log` |

### ⚠️ 真·运行时 MCP 配置不在代码仓库（2026-06-14 fibo 失联根因）

后端的 MCP server 列表（含 fibo / juzi / gangtise 等）**运行时不读仓库里的 `backend_dp/config/system/mcp_servers.json`**。路径由 `resolve_mcp_config_path()` 解析，优先级：`$MCP_CONFIG_PATH` → `$DPAGT_DATA_HOME/config/system/mcp_servers.json`。`backend_dp/.env` 把 `DPAGT_DATA_HOME` 钉死在 **`/opt/ablemind/dpagt-data`**，所以运行时真正读的是：

```
/opt/ablemind/dpagt-data/config/system/mcp_servers.json   ← 改这个才生效！
```

**改仓库里那份 `config/system/mcp_servers.json` 对运行进程零效果**（这是同一类「src 外运行时文件」坑，见 §2）。

- **典型事故**：fibo-mcp 从 ali-lab 本地搬到 ablework(`8.130.212.202:8113`)后，只改了仓库配置，运行时文件仍是旧的 `127.0.0.1:8113` → 本地无服务 → `ConnectError('All connection attempts failed')`，日志表象是 `MCP [fibo-mcp]: tool loading failed — unhandled errors in a TaskGroup`，后端 `MCP servers still missing ... giving up until next restart`。
- **排查铁律**：别信日志里的 server 名，要确认**进程实际在连哪个地址**。最快：`tcpdump -i any 'tcp port <端口>'`（连本地就抓 `-i lo`）看 SYN 目标；或用 live 进程的 env 跑 `resolve_mcp_config_path()` 打出真实路径。仓库文件、`/root/.dpagt`、`/opt/ablemind/dpagt-data` 三处都可能有同名文件，只有 `DPAGT_DATA_HOME` 那份算数。
- **改完**：`ssh ali-lab 'pm2 restart backend'`，等 ~30s 看日志 `MCP tools reloaded: N tools` 数字涨、`Registry: '<server>' → K tools` 出现即成功。防回归：部署脚本须把仓库 `config/system/` 同步到 `/opt/ablemind/dpagt-data/config/system/`，否则永久脱节。

### 黑盒测试后端 HTTP API（不必 SSH，公网带 token 直打）

排查"接口返回值/指标"类 bug 时，**不用进机器读源码**，直接拿用户 JWT 打公网 `ab.itseek.cc` 复现：

- **base**：`https://ab.itseek.cc`（nginx → ali-lab:8202）。鉴权：`Authorization: Bearer <JWT>`。
- **token 来源**：用户的 Casdoor JWT（~3000 字符，`eyJ…`），放在 **gitignore 的本地 env**（如 `yangnan/tmp/obsi/.env` 的 `ablemind_dp_token`）。**绝不写进本仓库/skill**，只存指针。
- 已验证端点：

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 探活 |
| GET | `/api/conversations` | 当前用户会话列表（`{conversations:[{id,title,message_count,…}]}`） |
| GET | `/api/conversations/{id}/messages` | 单会话全消息，**落库 metadata.usage 只有 5 字段**（见下） |
| POST | `/api/chat` | 聊天主入口，**SSE 流**；body 必填 `{"messages":[{"role":"user","content":"…"}]}`，省略 conversation_id = 全新会话 |

- **对照实验范式**（搞清某指标语义）：固定全新会话 + 单条消息，只改消息体大小，看指标怎么变。抓帧：
  `curl -sN -X POST -H "Authorization: Bearer $TOK" -H 'Content-Type: application/json' -d '{"messages":[{"role":"user","content":"…"}]}' https://ab.itseek.cc/api/chat | grep data-usage`

### ⚠️ token 指标的两个已查明事实（data-usage 帧 / 2026-06-19）

SSE `data-usage` 帧字段：`inputTokens / outputTokens / totalTokens / reasoningTokens / cachedInputTokens / cacheCreationInputTokens / cacheHitRatio / timestamp`。**注意落库的 `metadata.usage` 只存前 6 个里的 5 个，没有 `cacheHitRatio`/`reasoningTokens`** —— 这两个只在实时流里有，别拿落库数据找它们。

1. **`inputTokens` 可信**：对照实验（消息体 50→5k→40k→120k 字符）证明它**线性跟随真实输入**（斜率稳定），就是"实际喂给模型的总 token 数（含缓存前缀）"。多轮里偶尔"倒退"是真实的——那轮非缓存尾部（动态 system 尾巴/历史拼装/上轮回复长度）token 确实更少，**不是计数 bug**。`cachedInputTokens` 恒为 system prompt 长度（实测 117528，跨会话共享 provider 前缀缓存）。
2. **`cacheHitRatio` 是 BUG**：后端公式 = `cachedInputTokens / (inputTokens + cachedInputTokens)`，但 `inputTokens` 已含 `cachedInputTokens` → **分母重复计数**，把真实 ~99.9% 命中压到恒 ~0.5。**正确公式 = `cachedInputTokens / inputTokens`**。修这里。（实测：observed 与 `cached/(input+cached)` 四点逐位吻合，已证；大上下文 138744 处同样复现：显示 0.459、真实 0.849。）

### `data-context` 账本 + 上下文/压缩机制（2026-06-19 实测）

`data-context` 帧 = 后端发送前的 token 自算账本，字段：`system / tools / messages / summary / workspace / profile / knowledge / object / total`。要点：

- **缓存前缀的大头是 `tools`（~93k），不是 system（~24k）**。即"恒定 117528/117789"≈ system+tools，是 ~160 个 MCP 工具 schema 占的。想压成本，先砍工具数量。
- **`data-context.total` 与 `data-usage.inputTokens` 全程逐位相等**（单条 / 大消息 / agent 多轮工具累积都验过）→ 压缩触发指标本身可信，**没有账本错位**。
- **跨用户轮次的会话历史不累积进 prompt**：连发多轮，`inputTokens` 几乎不涨。模型的"记忆/回忆"走的是 **memory 工具（跨会话记忆文件）**，不是会话历史串接。所以单看多轮聊天，`inputTokens` 波动来自 per-turn 动态注入（memory 召回等），**不是历史在涨**。
- **真正撑大上下文的是单次 agent run 内的多次工具调用**：`messages` 槽随 tool 结果累积（实测一次 5 股票核实查询：118→7953→17270，total 117922→138744）。
- **压缩（`summary` 槽）触发阈值未实测到**：撑到 138744 仍 `summary=0` 且回答正常 → 模型真实上限远高于此（system+tools 已 118k，必跑 256k+ 模型），138k 未到阈值属合理，**不能据此断定压缩坏**。要验压缩需把单 run 硬撑到 ~200k+。

### memory 子系统：丢条 + 篡改值（2026-06-19，待修）

让模型在一个会话里连续记 8 条不同事实，复述时：**事实 1/3/8 整条丢失**，**事实 5「导师姓欧阳」被存成「姓陈」（值被改）**，并把其它会话的关键词串台泄漏进来。属抽取→落库→召回多组件配合失败导致的内容失真/丢失。排查方向：memory 写入的去重/抽取环节（疑似 LLM 抽取丢条 + 跨会话作用域未隔离）。

## 3. 各服务 env 前置（host `/opt/*/.env`，rsync 不覆盖）

- **skill-market**：`AI_API_KEY`(DashScope，后端 deepagents/ask/chat/Hub)、Casdoor 那组。
  `GITEA_ISSUE_REPO`/`ADMIN_EMAILS`(站内信/版主，可选)。
  > 已**不再需要** `NEXT_PUBLIC_AI_API_KEY` —— page-agent 改走服务端 `/api/llm` 代理(见 §4)。
- **portal**：`APP_BASE_URL`、Casdoor 那组。digest 数据源：
  `DIGEST_SOURCE_URL=/opt/portal/data/digests/digests.json`(门户读本地文件；spokane-3 的 cron 每日 rsync 更新它，
  落点在 deploy 的 `/data` 排除区、代码部署不覆盖)。**没设 → `/digest` 会空**。
  > 历史(已弃用)：`DIGEST_SOURCE_TOKEN` 走 GitHub contents API 拉私有库 raw —— 易 401、依赖 GitHub，已改 rsync。

## 4. 今天确立的架构 / 安全原则

- **密钥绝不进浏览器**。Next 里 `NEXT_PUBLIC_*` 会被内联进前端 bundle，匿名访客可扒。
  浏览器要调 LLM(如 page-agent)→ 走**服务端透传代理** `/api/llm/[...path]`：服务端注入 `AI_API_KEY` 转发 DashScope，
  流式原样透传 + 跨站 referer 403。浏览器 `baseURL` 指代理、`apiKey` 占位。官方实践就是如此(OpenAI SDK 的
  `dangerouslyAllowBrowser` 之名即警告)。代理还白赚限流/记账/可观测。
- **共享顶栏 = 一个 Web Component**(`portal/public/topbar.js`，托管 `ablemind.cc/topbar.js`)。
  三个服务(含第三方 gitea)都 `<script src>` 引入；导航数据/双语标签/高亮判定**只在这一个文件**。
  改菜单只改它 + 升 `?v=N`(§2)。Shadow DOM 自带样式，右侧登录态用 `slot` 各应用注入。
- **token 安全**：install_token 默认**只存 sha256、明文只现一次**(安全，但需"生成"按钮)。
  若要"登录即回填、无需生成"(像 `/data` 那样)，用**幂等 `ensureAccountToken`**：有(带明文)就复用、没有才铸一次并存明文；
  仅账户级便利凭证存明文(与 `ablework_tokens` 一致)，skill 安装 token 仍只存 hash。
- **登录闸门**(`server/access.ts`)：私域内容默认对匿名不可见。页面用 `getSession()` 渲染 LockedTeaser，
  API 用 `guardRead()` 兜底 401(防 curl 拖数据)；放行已登录用户或持有效 install_token 的 agent。
  > 副作用：匿名 `/data`、`/api/*` 会是 teaser/401 —— 验收时"匿名"用例预期要随之调整。
- **digest 数据与代码解耦**：门户运行时读本地 `digests.json`(`DIGEST_SOURCE_URL`，5min 缓存 + stale-while-error 兜底)。
  spokane-3 的 cron 每日生成后经 **Tailscale SSH rsync** 一个文件到 heyun01 `/opt/portal/data/digests/` 即更新——
  无 GitHub、无 token、无重部署。（早期用过 GitHub raw+PAT，因 401/依赖外部已弃用。）

## 5. 上线后验证工具箱

```bash
HOST=root@100.113.172.75
ssh $HOST 'systemctl is-active portal.service skill-market.service; cd /opt/gitea && docker compose ps'
for u in https://ablemind.cc/ https://ablemind.cc/digest https://skill.ablemind.cc/data \
         https://skill.ablemind.cc/connect https://ablemind.cc/digest/feed.json https://git.ablemind.cc/; do
  printf "%-42s " "$u"; curl -s -o /dev/null -w "%{http_code}\n" -m15 "$u"; done
```
- **登录态/私域页对未登录浏览器会被客户端 SSO 弹去登录**；`curl`(无 JS) 拿到服务端 200 原始 HTML ——
  用 `curl + grep 关键词` 验证内容最可靠。订阅源(`/digest/feed.json`、`/rss.xml`)必须对无 JS 客户端返真内容。
- **无头截图技巧**(本机 chromium，验证 UI)：
  - 私域页有 SSO 跳转 → `curl` 抓 HTML、`sed` 去掉 `<script>`、把 `/_next` 等改绝对(指 prod 或本地 server)、
    末尾只加回 `topbar.js` → 渲染本地 file:// 即可看真实布局，绕开登录。
  - 该 chromium 有 **500px 最小逻辑宽度**：`--window-size=390` 实际按 500 渲染，移动端截图按 500 看(别误判溢出)。
  - 入场动画用 `--force-prefers-reduced-motion=reduce` 关掉再截；跨域图片/字体可能让 `--virtual-time-budget` 早截。

## 6. 运维纪律

- **共享工作区**：常有多个会话的未提交 WIP 并存。提交只 `git add` 自己明确的文件，**别把别人的 WIP 一起 commit**；
  `git pull --rebase` 撞到未暂存改动就 autostash 或只推自己已提交的。
- **outward-facing 操作先确认**：改 prod `.env`/重启共享服务/push 到他人仓库 —— build+restart 在共享机 heyun01 上属 user-triggered，确认后再做。
- **回滚**：`git revert` + 重新 `deploy.sh`(无内置回滚)；build 失败会中断部署、服务保持旧版不中断。
- **每次改了部署逻辑/新增 src 外运行时文件 → 同步更新 `DEPLOY.md` 和本 skill。**

## 7. 统一登录（跨子域单会话）— 排障要点

症状「A 退出后 B 还登录 / 回 A 状态错乱」按序查四个缝（260610 全部踩过并修复）：
1. **两服务 `JWT_SECRET` 必须逐字节一致**（共享 `ablm_session` 由谁签都要能被对方验）。
   核对：`ssh heyun01 'for f in /opt/portal/.env /opt/skill-market/web/.env; do grep "^JWT_SECRET=" $f | sha256sum; done'` → 两行哈希必须相同。
2. **旧 host-only cookie 只删不读**：`getSession`/middleware 绝不回退读 `portal_session`/`skm_session` —— A 站登出物理上删不掉 B 站的 host-only cookie，回退读取=会话分裂。
3. **bfcache**：登录态是客户端 fetch，浏览器后退不重跑 effect → AuthStatus 须监听 `pageshow(persisted)` 重拉。
4. **`/api/auth/me` 必须 `Cache-Control: no-store`**。
其余不变式：会话/sso_tried/idt cookie 都带 `Domain=.ablemind.cc`；oauth_state 是 per-app host-only（正确）；
两边 `CASDOOR_CLIENT_ID` **可以不同**（同一 Casdoor 的两个应用，SSO 会话在 Casdoor 侧按用户共享，prompt=none 照样静默通过）。
