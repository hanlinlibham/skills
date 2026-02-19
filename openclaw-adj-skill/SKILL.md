---
name: openclaw-multi-agent
description: Configure and manage OpenClaw with 4 specialized agents (Shandian, Work, Research, Coding) including agent-to-agent communication, tool permissions, sandbox configuration, workspace setup, and permission management. Use when setting up multi-agent OpenClaw deployment, configuring agent permissions, creating agent memory files, managing sandbox settings, fixing permission issues, or troubleshooting agent connectivity.
---

# OpenClaw Multi-Agent Configuration

Multi-agent setup with 4 specialized agents coordinated through OpenClaw Gateway.

## Architecture

```
Gateway (ws://0.0.0.0:18789)
    ├── Shandian (main) ⚡️ - Coordinator, all tools
    ├── Work 💼 - Read-only, search
    ├── Research 🔬 - Read + browse, thinking model
    └── Coding 💻 - Read + write + execute
```

## Agent Configuration Details

### Shandian (main)
- **Role**: Coordinator
- **Model**: kimi-k2.5
- **Tools**: All (`["*"]`)
- **Sandbox**: Disabled (`"mode": "off"`)
- **Can spawn**: work, research, coding
- **Identity**: Main agent with full access, coordinates other agents

### Work
- **Role**: Safe operations
- **Model**: kimi-k2.5
- **Tools**: read, web_search, tavily_search, sessions_list, sessions_history (no write/exec)
- **Sandbox**: Disabled (`"mode": "off"`)
- **Safety**: Tool restrictions enforce read-only behavior

### Research
- **Role**: Deep analysis
- **Model**: kimi-k2-thinking (reasoning model)
- **Tools**: read, web_search, tavily_search, browser (no exec)
- **Sandbox**: Disabled (`"mode": "off"`)
- **Specialty**: Uses thinking model for complex analysis

### Coding
- **Role**: Technical implementation
- **Model**: kimi-k2.5
- **Tools**: read, write, edit, apply_patch, exec, bash, web_search
- **Sandbox**: Disabled (`"mode": "off"`)
- **Capabilities**: Full code execution

### Sandbox Configuration

**Current Status**: All agents have sandbox disabled

```json
"sandbox": {
  "mode": "off"
}
```

**Why Disabled**:
- Sandbox requires Docker-in-Docker (nested containers)
- OpenClaw container cannot access Docker daemon
- Attempting to enable causes: `Error: spawn docker EACCES`

**To Enable Sandbox** (requires container recreation):
```bash
# Mount Docker socket when creating container
docker run ... \
  -v /var/run/docker.sock:/var/run/docker.sock:rw \
  --group-add $(getent group docker | cut -d: -f3)
```

**Security Without Sandbox**: Tool permissions still enforce security boundaries
- Work cannot write or execute
- Research cannot execute code
- Only Coding has full execution access

## Directory Structure

### Configuration Path
```
/opt/1panel/apps/openclaw/openclaw/data/
├── conf/
│   ├── openclaw.json                    # Main configuration
│   └── agents/
│       ├── main/                        # Shandian (original "闪电")
│       │   ├── agent/
│       │   │   └── models.json         # Model configuration
│       │   └── sessions/               # Session storage
│       │       └── sessions.json       # Session index
│       ├── work/                        # Work agent
│       │   ├── agent/
│       │   │   └── models.json
│       │   └── sessions/
│       ├── research/                    # Research agent
│       │   ├── agent/
│       │   │   └── models.json
│       │   └── sessions/
│       └── coding/                      # Coding agent
│           ├── agent/
│           │   └── models.json
│           └── sessions/
└── workspace/                           # Agent workspaces
    ├── AGENTS.md                       # Shandian's workspace rules
    ├── SOUL.md                         # Shandian's identity
    ├── IDENTITY.md                     # Shandian's profile
    ├── work/                           # Work workspace
    │   ├── AGENTS.md
    │   ├── SOUL.md
    │   └── IDENTITY.md
    ├── research/                       # Research workspace
    │   ├── AGENTS.md
    │   ├── SOUL.md
    │   └── IDENTITY.md
    └── coding/                         # Coding workspace
        ├── AGENTS.md
        ├── SOUL.md
        └── IDENTITY.md
```

### Container Paths
Inside container, paths map to:
- Config: `/home/node/.openclaw/` (from host `conf/`)
- Workspace: `/home/node/.openclaw/workspace/` (from host `workspace/`)

## Permission Management

### Critical Permission Requirements

**All workspace files must be owned by `node:node` (UID 1000)**

```bash
# Check current permissions
ls -la /opt/1panel/apps/openclaw/openclaw/data/workspace/

# Fix permissions (run on host)
chown -R 1000:1000 /opt/1panel/apps/openclaw/openclaw/data/workspace/
chown -R 1000:1000 /opt/1panel/apps/openclaw/openclaw/data/conf/agents/

# Set correct permissions
chmod -R 700 /opt/1panel/apps/openclaw/openclaw/data/conf/agents/
chmod -R u+rw /opt/1panel/apps/openclaw/openclaw/data/workspace/
```

### Permission Errors

**Error**: `EACCES: permission denied, open '/home/node/.openclaw/workspace/AGENTS.md'`

**Cause**: Files owned by `root:root` instead of `node:node`

**Solution**: Run permission fix commands above, then restart container

### Container User
- OpenClaw runs as `node` user (UID 1000, GID 1000)
- Files must be readable/writable by this user
- Docker volumes inherit host UID/GID

## Key Configuration Sections

### Main Config (openclaw.json)

Location: `/opt/1panel/apps/openclaw/openclaw/data/conf/openclaw.json`

**Required sections**:

1. **Agents List** (`agents.list`):
```json
{
  "id": "main",
  "name": "Shandian",
  "default": true,
  "identity": {
    "name": "Shandian",
    "emoji": "⚡️"
  },
  "workspace": "/home/node/.openclaw/workspace",
  "agentDir": "/home/node/.openclaw/agents/main/agent",
  "model": "moonshot/kimi-k2.5",
  "sandbox": { "mode": "off" },
  "tools": { "allow": ["*"] }
}
```

2. **Agent-to-Agent Communication** (`tools.agentToAgent`):
```json
"tools": {
  "agentToAgent": {
    "enabled": true,
    "allow": ["work", "research", "coding"]
  }
}
```

3. **Bindings** (`bindings`):
```json
"bindings": [
  {
    "agentId": "main",
    "match": { "channel": "telegram" }
  }
]
```

4. **Gateway** (`gateway`):
```json
"gateway": {
  "port": 18789,
  "mode": "local",
  "bind": "lan",
  "trustedProxies": ["172.18.0.1", "127.0.0.1"],
  "auth": {
    "mode": "token",
    "token": "your-secure-token"
  }
}
```

### Model Configuration

Each agent has `models.json` in their `agent/` directory:

```json
{
  "providers": {
    "moonshot": {
      "baseUrl": "https://api.moonshot.cn/v1",
      "api": "openai-completions",
      "apiKey": "${MOONSHOT_API_KEY}",
      "models": [
        {
          "id": "kimi-k2.5",
          "name": "Kimi K2.5",
          "contextWindow": 256000,
          "maxTokens": 32768
        }
      ]
    }
  }
}
```

## Memory Files

Each workspace contains identity files loaded on agent startup:

### SOUL.md
Agent's core identity, capabilities, and team awareness:
- **Name, Role, Emoji**: Agent identity
- **Who You Are**: Personality and capabilities
- **Your Teammates**: Other agents and collaboration
- **Boundaries**: Tool restrictions and limitations

### IDENTITY.md
Concise profile summary:
- Name, creature type, role
- Team members
- Specialty and limitations
- Principles

### AGENTS.md
Workspace rules and operational guidelines

### TOOLS.md
Tool-specific configurations and preferences

## Setup Script

Use `scripts/setup-agents.sh` to create complete structure:

```bash
# Run as root
sudo ./scripts/setup-agents.sh /opt/1panel/apps/openclaw/openclaw/data
```

**Creates**:
- Agent directory structure (main, work, research, coding)
- models.json files for each agent
- Complete SOUL.md and IDENTITY.md templates
- Correct permissions (1000:1000)

## Remote Client Connection

### Environment Variables
```bash
export OPENCLAW_INSTANCES='{
  "main": {
    "url": "ws://server-ip:8789",
    "token": "your-token",
    "label": "闪电助手"
  }
}'
```

### SSH Tunnel (Recommended)
```bash
ssh -N -L 8789:localhost:8789 user@server
export OPENCLAW_GATEWAY_URL="ws://localhost:8789"
export OPENCLAW_GATEWAY_TOKEN="your-token"
```

## Telegram Integration

**@mention routing**:
- `@shandian` / `@闪电` / `@lightning` / `@main` → Main agent
- `@work` / `@工作` / `@办公` → Work agent
- `@research` / `@研究` / `@调研` / `@分析` → Research agent
- `@code` / `@coding` / `@编程` / `@代码` / `@dev` → Coding agent

**Default**: Routes to `main` (Shandian)

## Important Notes

### Shandian = Original "闪电"
- All history preserved in `agents/main/sessions/`
- Original workspace at `workspace/` (root level)
- Renamed from `main` to `Shandian` for clarity
- Still uses `agentId: "main"` for compatibility

### Agent Isolation
- Each agent has separate session storage
- Separate workspace directories
- Independent tool permissions
- No shared memory between agents (by design)

### Tool Permissions Enforce Security
Even without Docker sandbox:
- Work cannot write files or execute code
- Research cannot execute code
- Coding has full access but respects user boundaries
- Shandian can coordinate but respects tool restrictions

### Session Management
- Sessions stored in `agents/{id}/sessions/`
- Each agent maintains independent conversation history
- Sessions indexed in `sessions.json`
- Session files: `{session-id}.jsonl`

## Troubleshooting

### 1012 Service Restart Error
**Cause**: Token mismatch between client and server
**Fix**: Verify `OPENCLAW_GATEWAY_TOKEN` matches server config

### Permission Denied (EACCES)
**Cause**: Files owned by `root:root` instead of `node:node`
**Fix**:
```bash
chown -R 1000:1000 /opt/1panel/apps/openclaw/openclaw/data/workspace/
docker restart 1Panel-openclaw-F90J
```

### Agent Not Showing in UI
**Cause**: Missing `identity` section in agent config
**Fix**: Add `identity: { name: "...", emoji: "..." }` to agent definition

### Spawn Docker EACCES
**Cause**: Agent configured with `"sandbox": {"mode": "all"}` but Docker unavailable
**Fix**: Disable sandbox: `"sandbox": {"mode": "off"}`

### WebSocket Connection Refused
**Check**:
1. Container running: `docker ps | grep openclaw`
2. Port exposed: `docker port 1Panel-openclaw-F90J`
3. Firewall: `sudo ufw status` (should allow 8789)

### Config Invalid Errors
**Validate JSON**:
```bash
python3 -m json.tool /opt/1panel/apps/openclaw/openclaw/data/conf/openclaw.json > /dev/null && echo "Valid JSON"
```

### Agent History Not Loading
**Check**: Session files exist in `agents/{id}/sessions/`
**Fix**: Ensure correct ownership (1000:1000)

## Maintenance Commands

```bash
# Restart OpenClaw
docker restart 1Panel-openclaw-F90J

# View logs
docker logs 1Panel-openclaw-F90J --tail 50

# Check agent sessions
docker exec 1Panel-openclaw-F90J ls -la /home/node/.openclaw/agents/main/sessions/

# Verify permissions
docker exec 1Panel-openclaw-F90J ls -la /home/node/.openclaw/workspace/

# Check config
docker exec 1Panel-openclaw-F90J cat /home/node/.openclaw/openclaw.json | python3 -m json.tool
```

See `references/openclaw-multi-agent.json` for complete configuration template.
