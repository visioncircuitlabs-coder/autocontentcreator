# How to run the demo

You will open **Make today’s post** on http://localhost:3050 and walk Look → Pick → Make → Your call → Preview.

## Prerequisites

- This folder: `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design`
- Docker **or** Python 3.12 + Node 22 already installed
- Optional: `XAI_API_KEY` in `.env` for Grok copy and Grok Imagine. Empty keys still walk on templates and a Pillow card.

## Docker (from this worktree)

```text
copy .env.example .env
docker compose up --build
```

macOS/Linux: `cp .env.example .env` then the same compose command.

- Walk: http://localhost:3050
- Health: http://localhost:8000/health

Port 3050 is on purpose (3000 is often taken).

## Without Docker (PowerShell)

API:

```text
cd apps\api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
uvicorn main:app --host 127.0.0.1 --port 8000
```

Web (other terminal):

```text
cd apps\web
npm install
$env:NEXT_PUBLIC_API_URL = "/engine"
$env:ENGINE_URL = "http://127.0.0.1:8000"
npx next dev --hostname 127.0.0.1 --port 3050
```

To force Grok Imagine (if `.env` still says stub):

```text
$env:IMAGE_GEN_MODE = "imagine"
$env:IMAGE_GEN_MODEL = "grok-imagine-image"
$env:CHAT_MODEL = "xai/grok-4.6"
```

Set those on the **API** process, then restart uvicorn.

## Verification

1. http://localhost:8000/health shows `"ok": true`
2. http://localhost:3050 shows **Look for ideas**
3. Optional: `python scripts/demo_walk.py` from the worktree root (skips if API is down)

## Troubleshooting

| What you see | What to do |
|---|---|
| News engine is not running | Start the API on 8000, keep Next on 3050 |
| Too many searches | Wait a minute |
| That took too long | Try again. Look + Make + picture share a 5-minute page wait |
| Dark card instead of a photo | Imagine is off or the key failed. Check `IMAGE_GEN_MODE` on the API process |
| Nothing worth a closer look | Use **Use a sample idea (practice)** |

Employee steps after it is up: [runbooks/make-a-post.md](runbooks/make-a-post.md).
