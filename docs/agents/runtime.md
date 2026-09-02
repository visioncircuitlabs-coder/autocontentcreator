# Runtime

## Worktree

Product checkout:

```text
D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design
```

Branch `feat/foolproof-design`. `main` at the repo root can still look like design-only. Do not scaffold there.

Stay on **D:**. C: is full. Put caches under `D:\PROJECTS\autocontentcreator\.cache\` (OpenCode XDG, pip, etc.). Feature isolation: more dirs under `.worktrees/`.

A worktree’s `.git` is a **file** (`gitdir: …`), not a folder. Do not robocopy `/XD .git` expecting a directory — you can point a review worktree at the wrong tree.

## Ports

| What | Where |
|---|---|
| Walk | http://localhost:3050 |
| API | http://127.0.0.1:8000 |
| Health | http://127.0.0.1:8000/health → `{"ok": true, "chat": bool}` |
| Events | http://localhost:3050/engine/events |
| Compose web inside container | 3000, published as 3050 |

Port 3000 is often taken on this PC. **3050 is on purpose.**

## Env

Template: `.env.example`. Local: `.env` (gitignored).

| Variable | Effect |
|---|---|
| `APP_TZ` | `Asia/Kolkata` |
| `SQLITE_PATH` | SQLite file. Compose forces `/data/demo.db` |
| `LOG_PATH` | JSONL. Compose `/data/logs/machine.jsonl` |
| `CHAT_MODEL` | Default `xai/grok-4.6` |
| `CHAT_TIMEOUT_S` | LiteLLM completion timeout. Default `180` |
| `IMAGE_TIMEOUT_S` | Grok Imagine HTTP timeout. Default `600` (10 minutes) |
| `XAI_API_KEY` | Grok chat + Imagine + optional Grok web fetch |
| `GEMINI_API_KEY` / `GROQ_API_KEY` | Alternate chat |
| `IMAGE_GEN_MODE` | `imagine` \| `stub` \| `http` |
| `IMAGE_GEN_MODEL` | `grok-imagine-image-2.0` (stale `grok-imagine-image` maps to 2.0) |
| `IMAGE_GEN_URL` / `IMAGE_GEN_KEY` | Only for `http` mode |
| `NEXT_PUBLIC_API_URL` | Browser origin. Walk uses `/engine` |
| `ENGINE_URL` | Server-side proxy target (`http://127.0.0.1:8000` or `http://api:8000`) |

**Mismatch trap:** `.env` may still say `IMAGE_GEN_MODE=stub` while a manual uvicorn was started with `imagine` in the process env. The **process** wins. After a naive restart, you silently get the Pillow card. Set the file *or* export the var every launch. `.env.example` is `imagine`.

Empty chat keys → templates. Missing Imagine key → stub card after a warning, not a blank preview.

## Docker

From this worktree:

```text
copy .env.example .env
docker compose up --build
```

Root `docker-compose.yml` includes `infra/docker-compose.yml`. Volume `./data` → `/data`. Web build args set `/engine` and `ENGINE_URL=http://api:8000`.

## Without Docker (this laptop’s usual walk)

API (from `apps/api`), load `.env` into the process, then:

```text
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Web:

```text
cd apps\web
$env:NEXT_PUBLIC_API_URL = "/engine"
$env:ENGINE_URL = "http://127.0.0.1:8000"
npx next dev --hostname 127.0.0.1 --port 3050
```

Force Imagine even if `.env` says stub:

```text
$env:IMAGE_GEN_MODE = "imagine"
$env:IMAGE_GEN_MODEL = "grok-imagine-image-2.0"
$env:CHAT_MODEL = "xai/grok-4.6"
```

Kill whatever already owns 8000 before restarting. Two uvicorns = stale overlay/prompt.

## Time budget

The page waits **11 minutes** (`maxDuration = 660`, proxy abort 660s) so a 10-minute Imagine call can finish. Look + Make + Imagine all share that if they go through `/engine`.

What eats it: sequential Grok scores, factory loop (writer + judge + craft × rounds), Imagine up to 600s. That is why photos are not made on Pick.

## Data you must not commit

`data/demo.db`, `data/images/*.png`, `data/exports/*.zip`, `data/logs/machine.jsonl`, `.env`, `.cache/`, `.venv/`, `node_modules/`.

## Telegram

Off. Do not wire a send-to-Telegram path without a decision note. Export is a ZIP download.
