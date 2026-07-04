---
name: app-publish
description: >
  在本机(yangnan 工作区)把一个小型 web 应用从零发布到公网的标准 playbook。
  覆盖:选空闲端口、复用现成 .env 密钥(非明文)、pm2 托管 + 开机自启、
  Cloudflare Tunnel 挂子域/路径拿自动 HTTPS(不开公网端口)、口令 cookie 网关、
  交付前实测与结构整理。含两个真实踩过的坑(pm2 默认目录 root 占用、
  Cloudflare 不剥路径前缀)和一份发布前 checklist。
  当需要把一个本地小工具/演示页/内部应用上线到公网、配 pm2 持久化、
  挂 lihanlin.com 子域、加访问口令时使用。
  触发词:发布、上线、deploy、部署小应用、挂域名、Cloudflare Tunnel、隧道、
  pm2 持久化、加 HTTPS、内网工具上公网、加口令登录。
---

# 小应用发布手册（app-publish）

把一个单文件级别的 web 应用（FastAPI/Flask/Node 皆可）发布到公网的可复用流程。
2026-06-25 用 `receipt-ocr`（截图结构化解析，`workspace/260625/output/receipt-ocr/`）跑通。
跨会话背景见记忆 `small-app-publish-playbook` 与 `pm2-home-root-owned`。

> 原则：**不要裸 IP + 明文 HTTP 上公网**。本机有现成 Cloudflare Tunnel，挂子域即得 HTTPS、不开端口。

## 0. 拓扑速记

- pm2 自定义目录：`PM2_HOME=/home/core/dev/yangnan/.pm2`（默认目录 root 占用，见坑①）
- Cloudflare Tunnel：config `/etc/cloudflared/config.yml`，绑域名 `lihanlin.com`，
  tunnel id `fc956cd5-de60-4cf3-9116-f47cbf23a02f`，cert.pem 在 `~/.cloudflared/`
- 视觉/LLM 密钥：`.agents/skills/.env`（`DASHSCOPE_API_KEY` 等）
- passwordless sudo 可用（`sudo -n true` 通过）

## 1. 发布流程（按顺序）

### 第 1 步 选端口 + 写应用
```bash
ss -tlnp 2>/dev/null | grep -oE ':[0-9]+' | sort -u    # 看占用，挑个空闲端口
```
- 小工具：单进程 FastAPI 同时托管页面 + 接口即可。
- **支持 `URL_PREFIX` 环境变量**（见坑②）：路由、表单 action、fetch URL、cookie path 都要能带前缀。
- 密钥从现成 `.env` 读，**非明文校验**（只报 set/not set，绝不打印进日志或前端）。
- 监听 `0.0.0.0:<port>`（隧道从 localhost 转发，不直接对公网开端口）。

### 第 2 步 pm2 托管 + 开机自启
写 `ecosystem.config.js`（含 `cwd` 和 `env`）：
```js
module.exports = { apps: [{
  name: "myapp", script: "app.py", interpreter: "python3",
  cwd: "/abs/path/to/app",
  env: { LOGIN_PASSWORD: "...", URL_PREFIX: "/myapp" },
  autorestart: true, max_restarts: 10,
}]};
```
```bash
export PM2_HOME=/home/core/dev/yangnan/.pm2          # 坑① 必须
pm2 start ecosystem.config.js && pm2 save
# 开机自启（systemd），生成后必须改 PM2_HOME（坑①）：
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u core --hp /home/core
sudo sed -i 's#/home/core/.pm2#/home/core/dev/yangnan/.pm2#g' /etc/systemd/system/pm2-core.service
sudo systemctl daemon-reload && sudo systemctl enable pm2-core
# 验证开机路径：pm2 kill → sudo systemctl start pm2-core → 应用应自动 resurrect
```
> 改了 ecosystem 的 env 要 `pm2 restart ecosystem.config.js --update-env`（裸 `--update-env` 只读 shell env，不读文件）。

### 第 3 步 上公网（Cloudflare Tunnel）
```bash
sudo cp /etc/cloudflared/config.yml /etc/cloudflared/config.yml.bak.$(date +%s)
# 在 catch-all 404 前插入 path 限定规则（留子域给后续用途）：
#   - hostname: app.lihanlin.com
#     path: ^/myapp
#     service: http://localhost:<port>
cloudflared tunnel route dns fc956cd5-de60-4cf3-9116-f47cbf23a02f app.lihanlin.com
sudo systemctl restart cloudflared
curl -s -o /dev/null -w "%{http_code}\n" https://app.lihanlin.com/myapp/   # 期望 200
```

### 第 4 步 访问控制
- 至少一道口令网关：cookie 令牌 = `sha256(口令 + 固定盐)`（重启不掉登录、改口令自动失效）。
- 提醒用户：单口令 + 无频率限制只是轻量防护，敏感数据建议上 Cloudflare Access（SSO/邮箱闸门）。

### 第 5 步 交付前
- **端到端实测**延迟/精度（别拍脑袋；LLM 应用真瓶颈常在模型档位 + 输出 token，不在本地代码）。
- 内联 HTML/CSS/JS 抽到 `templates/`，主程序只留干净逻辑，分区注释。

## 2. 必须记住的坑（都真实踩过）

**① pm2 默认目录 `/home/core/.pm2` 是 root 所有** → core 跑 pm2 报 `EACCES`。
所有 pm2 命令带 `export PM2_HOME=/home/core/dev/yangnan/.pm2`；`pm2 startup` 生成的 systemd unit
会把 `PM2_HOME`/`PIDFile` 硬编码成默认值，**必须手动 sed 改**指向自定义 home。

**② Cloudflare Tunnel 不剥路径前缀** → `app.lihanlin.com/myapp` 原样打到 `localhost:<port>/myapp`。
应用必须在 `/myapp` 前缀下提供服务，否则全 404。用 `URL_PREFIX` 统一处理路由/action/fetch/cookie-path。

**③ 用后台进程别在启动命令里 `pkill -f app.py`** → 会误杀执行该命令的 wrapper shell 自身（命令行含 "app.py"）。
杀进程改用按端口定位 pid，或交给 pm2。

**④ 前端从 Python 三引号搬到独立 `.html` 文件时，转义要降级**：
Python 串里的 `\\'` 在真文件里应是单反斜杠 `\'`。搬完用 `node --check` 校验内联脚本。

## 3. 发布后验证清单

- [ ] `https://<域名>/<前缀>/` 返回 200，登录页正常
- [ ] 错误口令 401、正确口令 303 种 cookie、带 cookie 进主页
- [ ] 核心接口端到端跑通（带真实样本）
- [ ] 未登录访问受保护接口 → 401
- [ ] 非前缀路径（如裸子域 `/`）→ 404（确认 path-scoped 生效）
- [ ] `pm2 kill` → `systemctl start pm2-core` → 应用自动 resurrect（开机自启验证）
- [ ] 密钥未出现在日志 / 前端 / 报错信息里

## 4. 日常运维

```bash
export PM2_HOME=/home/core/dev/yangnan/.pm2
pm2 list                                  # 状态
pm2 logs <name>                           # 日志
pm2 restart ecosystem.config.js --update-env && pm2 save   # 改代码/改 env 后
```
- 改口令：编辑 ecosystem 的 `LOGIN_PASSWORD` → 上面这条 restart。
- 改样式/文案：编辑 `templates/*.html` → `pm2 restart <name>`。
