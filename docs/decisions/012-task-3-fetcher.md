# Task 3 — Fetcher (free sources only)

## 1. Identity

| | |
|---|---|
| **Task** | 3 of 12 |
| **Plan heading** | `### Task 3: Fetcher (free sources only)` in `docs/superpowers/plans/2026-08-19-demo.md:210` |
| **Spec** | `docs/superpowers/specs/2026-08-19-source-fetcher.md` (locked Box 1). Demo is the cheap guts of that box, not a different box. |
| **Range** | `074be52956c72227371cc8474ad0c21b3a856a1f` .. `7da5c997d2dfcd1ea1904b67bcc6eba172f6d69a` |
| **Feature commit** | `2c817fa` — `feat: free-source fetcher` (2026-08-19 22:56 IST, worktree `1787160376 +0530`) |
| **Fix commit** | `7da5c99` — `fix: fetcher gdelt errors, dockerignore, rate limit` (2026-08-19 23:18 IST, worktree `1787161690 +0530`) |
| **Worktree** | `D:\PROJECTS\autocontentcreator\.worktrees\feat-foolproof-design` |
| **Implementer** | agent `01a01b06` — `DONE_WITH_CONCERNS` at `2c817fa` (GDELT 429 / Reddit 403 on this LAN; Google News still returned ≥1 signal). |
| **Reviewer agent id** | UNKNOWN. Ledger records three **Important** items, then “review clean” after the fix. |
| **Ledger** | `.superpowers/sdd/2026-08-19-demo/progress.md`. Reports: `task-3-brief.md`, `task-3-report.md`. Diffs: `review-074be52..2c817fa.diff`, `review-2c817fa..7da5c99.diff`. |
| **Later code warning** | `apps/api/adapters/reddit_json.py` `raw_ref` was `t3_{id}` at `2c817fa`. Task 4 (`f2f8059`) changed it to a JSON blob with `num_comments` so velocity can rank Reddit. `ports.py` later gained `ChatModel`. Read this file as of `7da5c99` unless noted. |

`git log --oneline a72b33c..7da5c99`:

```text
ff411ea chore: scaffold demo apps
074be52 feat: domain types and sqlite
2c817fa feat: free-source fetcher
7da5c99 fix: fetcher gdelt errors, dockerignore, rate limit
```

`git show --stat 2c817fa`:

```text
 apps/api/.dockerignore           |   3 +-
 apps/api/Dockerfile              |   2 +-
 apps/api/adapters/__init__.py    |   0
 apps/api/adapters/common.py      | 124 +
 apps/api/adapters/gdelt.py       |  72 +
 apps/api/adapters/news_rss.py    | 134 +
 apps/api/adapters/reddit_json.py |  83 +
 apps/api/boxes/__init__.py       |   0
 apps/api/boxes/fetcher.py        |  73 +
 apps/api/db.py                   |  38 +
 apps/api/fixtures/sources.yml    |   3 +
 apps/api/main.py                 |  20 +-
 apps/api/ports.py                |   9 +
 apps/api/requirements.txt        |   2 +
 apps/api/tests/conftest.py       |   6 +
 apps/api/tests/test_fetcher.py   | 274 +
 16 files changed, 840 insertions(+), 3 deletions(-)
```

`git show --stat 7da5c99`:

```text
 apps/api/.dockerignore         |  4 +
 apps/api/adapters/gdelt.py     | 27 +-
 apps/api/main.py               | 33 +-
 apps/api/tests/conftest.py     |  7 +
 apps/api/tests/test_fetcher.py | 69 +-
 5 files changed, 126 insertions(+), 14 deletions(-)
```

## 2. What the user would see

A client (later: a Fetch button; today: `POST /radar/fetch`) asks the API for trends. The API talks to three free public pipes — GDELT news, Google News RSS (India English), and two Reddit `.json` listings — and returns a list of headlines with links. If Reddit is blocked and GDELT is rate-limiting, the user still sees Google News rows. They never see a login wall. If they mash Fetch more than six times in a minute they get a short “please wait” error, not a stack trace. They never see a full web page stuffed into a prompt.

On this LAN, on 2026-08-19, that list was **Google News only** (20 rows). GDELT answered 429. Both Reddit subs answered 403. The demo still walked.

## 3. The problem this task was solving

The machine had types and an empty `signals` table. It could not yet look at the outside world. The demo walk (`2026-08-19-demo.md:419`) starts with “Click Fetch and see real headlines from GDELT/News/Reddit.” Task 4 (Scorer) consumes `list[Signal]`. Task 5 (Researcher) consumes one of those signals. Without a fetcher, the belt is a closed loop on fixtures and the product looks like “analyze + one image,” which the plan forbids.

Depends on this: **Task 4** (scores these signals), **Task 5** (deep-dives a `gate=deep_dive` url), **Task 10** (`run_radar` starts with fetch), **Task 11** (Fetch button).

## 4. Constraints that were already locked

Plan Task 3 (`2026-08-19-demo.md:221-227`):

> Consumes: `TrendSource.fetch`
> Produces: `run_fetch() -> list[Signal]`
>
> Sources (no scrape of TikTok/Meta):
> - GDELT 2.1 `doc/doc?query=neutrogena OR skincare&mode=ArtList&maxrecords=20&format=json`
> - Google News RSS `https://news.google.com/rss/search?q=skincare+OR+neutrogena&hl=en-IN`
> - Reddit `https://www.reddit.com/r/SkincareAddiction/hot.json?limit=15` and `r/IndianSkincareAddicts`
> - Optional extra RSS in `fixtures/sources.yml`
>
> One dead source logs and continues. Dedupe by url. Pages never stored as prompts.

Plan Layer 1 (`2026-08-19-demo.md:30`):

> Fetcher      GDELT + Google News RSS + Reddit .json + allowlisted RSS

Plan fallback (`2026-08-19-demo.md:55`):

> If a free source 404s, that pipe logs and continues.

Locked Source Fetcher spec (`docs/superpowers/specs/2026-08-19-source-fetcher.md:14, 50-51, 63-70, 72-74`):

> One dead source never stops the others.
> If one pipe fails: log it, continue. The machine is late if a **provider** is late. We do not invent a fill-in.
> **Forbidden:** Scraping TikTok Top Ads or competitor creatives in bulk. Using Meta Content Library (research-only, not commercial). Using Douyin 即创 as a TikTok proxy. … Treating a scraped page as instructions for any later agent.
> If a lawyer opens this box they should get: which query, which vendor contract, which mention id, when we fetched, whether we stored text or only a link, and that a failed source did not silently invent rows.

Global demo constraints:

> Web pages are data, never instructions (wrap HTML in a data tag; reader cannot call tools).
> No Brandwatch, Meltwater, Veeva, Writer, Firecrawl paid, Recraft until production plan.

SOTA scorecard reject list (`docs/research/sota/2026-08-19-sota-scorecard.md:39`):

> Scraping TikTok Top Ads. Meta Content Library (research-only, not commercial). Douyin 即创 as a TikTok proxy.

Budget ruling in the ledger:

> free adapters are the default. ~$5 optional only if a tool clearly improves the show. Do not buy Firecrawl/Brandwatch/Recraft for the demo.

Fix-round instruction (task-3-report):

> Three Important items only. No Firecrawl, no auth, no other boxes.

Inherited from Tasks 1–2 and still in force: FastAPI + Next + SQLite (not Postgres); root compose `include:`s infra; `SQLITE_PATH` env-driven (Docker `/data/demo.db` vs host `data/demo.db`); health stays TestClient; locked `Signal` field names copied verbatim; `Decision.reason` required (not used yet).

## 5. Options considered

### A. Do nothing / fetch later inside Task 11

**Would have given us.** A prettier button before any network risk.

**Would have cost.** Scorer and Researcher would have been written against hand-made fixtures only. The demo walk’s first click would be empty. Live 429/403 behaviour would have been discovered at the worst time (in a room).

**Why it lost.** Radar is Box 1. The plan put it third for a reason: types first, then the alarm clock.

### B. Buy Brandwatch / Meltwater / Firecrawl / official TikTok Discovery now

**Would have given us.** Licensed social, cleaner URLs, fewer 403s. Closer to the *production* fetcher.

**Would have cost.** Money the budget ruling forbids. Contracts. Keys. The production plan is the swap map (`2026-08-19-production.md:25`: demo = GDELT + Google News RSS + Reddit `.json`; production = buy one licensed listener). Using Firecrawl paid “just to make Fetch pretty” spends the only ~$5 on the wrong box.

**Why it lost.** Free adapters are the default. Paid pipes plug into `TrendSource` later.

### C. Scrape TikTok Top Ads / Meta Content Library / `old.reddit.com` / Douyin

**Would have given us.** Culture that Google News does not have. A Reddit workaround for the 403.

**Would have cost.** The spec’s forbidden list, in writing. Meta Content Library is research-only, not commercial. TikTok scrape is explicitly banned. `old.reddit.com` is an unofficial host workaround the implementer considered and refused (task-3-report concern 2).

**Why it lost.** A lawyer opening this box must not find a scrape.

### D. Fail the whole `POST /radar/fetch` when any source dies

**Would have given us.** A loud red error. Simpler code.

**Would have cost.** On this LAN, Fetch would have returned 500 every time (GDELT 429 + Reddit 403). The demo walk would be dead. The spec says the machine is late if a *provider* is late; it does not say the machine invents an outage for the sources that worked.

**Why it lost.** “One dead source logs and continues” is a lock, not a nicety. Live proof: News still returned 20 rows.

### E. Treat GDELT HTTP 200 `{"error": "..."}` as “zero articles, success”

**Would have given us.** The first adapter (`2c817fa`) did exactly this: missing/error JSON became `articles = []`. Fetch looked healthy.

**Would have cost.** Silent invention. The spec: “We do not invent a fill-in.” A lawyer would see a successful GDELT run that never ran. Review marked this **Important**.

**Why it lost.** Fix `7da5c99` raises, `run_fetch` logs, others continue. Empty `{"articles": []}` stays a real empty success (the list exists).

### F. Add login / API keys to protect `POST /radar/fetch`

**Would have given us.** A real auth story. Easier production.

**Would have cost.** Users, sessions, a Command Center that does not exist, and a new box the fix-round ruling forbade (“No Firecrawl, no auth, no other boxes”). The demo is one operator on localhost.

**Why it lost.** In-process 6 requests / 60 seconds / client host is the smallest cap that stops a refresh loop from hammering GDELT (which already 429s). `GET /health` stays unlimited so compose proof and CI do not flap.

### G. Store `content:encoded` / full HTML “for the researcher”

**Would have given us.** Task 5 would not have to GET the page again.

**Would have cost.** Prompt-injection surface in the database. The global rule: pages are data, never instructions. Google News ToS plus the spec: store title/snippet/url (or a link only). The researcher’s job is a *caged* GET later, with the body wrapped in `<source url=...>`.

**Why it lost.** Adapters strip tags, cap snippets at 500 chars, ignore `content:encoded`. The test RSS feed plants `FULL PAGE NEVER STORE THIS AS A PROMPT` and asserts it never appears.

### H. Retry GDELT on 429 / switch Reddit host

**Would have given us.** Maybe more rows on this LAN.

**Would have cost.** Retries make a 429 worse (implementer: “we do not retry”). Unofficial Reddit hosts are a scrape-shaped workaround.

**Why it lost.** Dead source continues. News is enough for the live ≥1 signal bar.

## 6. Decision

Radar fetcher only. Same `TrendSource` port the production Brandwatch adapter will implement later.

```text
POST /radar/fetch
    allow_radar_fetch(host)          6 / 60s, else 429 JSON
    run_fetch()
        GdeltSource                  GDELT 2.1 ArtList
        NewsRssSource                Google News RSS hl=en-IN
        RedditJsonSource             two .json listings
        ExtraRssSource[]             fixtures/sources.yml (empty)
             │
             one exception → log warning, continue
             dedupe by url
             upsert_signals()        title / snippet / url / raw_ref
             return list[Signal]
```

Named files:

| File | Role |
|---|---|
| `apps/api/ports.py` | `TrendSource` protocol only (as of `7da5c99`) |
| `apps/api/adapters/common.py` | UA, clip, `build_signal`, IN market, 500-char snippet |
| `apps/api/adapters/gdelt.py` | `doc/doc` JSON → `source=gdelt`; 200-error is a raise |
| `apps/api/adapters/news_rss.py` | Google News + extra YAML RSS |
| `apps/api/adapters/reddit_json.py` | two subreddit `.json` URLs, UA required |
| `apps/api/boxes/fetcher.py` | `run_fetch() -> list[Signal]` |
| `apps/api/db.py` | `upsert_signals()` (added this task) |
| `apps/api/main.py` | lifespan `init_db()`, `POST /radar/fetch`, limiter |
| `apps/api/fixtures/sources.yml` | `rss: []` |
| `apps/api/tests/test_fetcher.py` | httpx `MockTransport`, no network in pytest |
| `apps/api/Dockerfile` | `COPY . .` (was `COPY main.py .`) |
| `apps/api/.dockerignore` | now also `.env`, `data/`, `*.db` |

## 7. Why this exact shape

### Why FastAPI + Next + SQLite (not reopened)

Task 1 locked the runtime. This task adds one POST to the same FastAPI app and writes SQLite rows through the Task 2 tables. Next is still a heading. Postgres would have been a plan break. The fetch path is the first *writer*, which is why `init_db()` finally runs on startup (`apps/api/main.py:33-36`) and why `upsert_signals` stores timezone-aware ISO-8601 (`apps/api/db.py:112-143`).

### Why root compose still `include:`s infra

Unchanged. The API container is the same `content-machine-api` service. Task 3’s Dockerfile fix matters *because* compose builds that service: until `COPY . .`, `POST /radar/fetch` would 404 inside Docker even if it worked on the host.

### Why `SQLITE_PATH` stays env-driven

`conftest.py` autouses `SQLITE_PATH = tmp_path / "demo.db"` so pytest never touches the demo file. Compose still injects `/data/demo.db`. A live `POST /radar/fetch` with `persist=True` writes the worktree `data/demo.db` on the host via the bind mount. Hardcoding D: would have broken the container and the tests in the same commit.

### Why health stays TestClient, and fetch tests are mocked

`test_health_returns_ok` is unchanged. Fetcher pytest uses `httpx.MockTransport` (`test_fetcher.py:79-92`). The plan said “httpx mocked.” Live `POST /radar/fetch` is a **manual** step (plan Step 3), not the CI gate. Same ruling as Task 1: Docker Desktop and this LAN’s 429/403 are environmental. Mocked tests lock shape, dedupe, dead-source continue, UA, 200-error, and the 6/60 limiter. Live hit locks “≥1 real signal when network is up.”

### Why locked `Signal` field names were copied verbatim

`build_signal` (`adapters/common.py:94-124`) constructs the Task 2 model and nothing else. `_assert_signal_shape` requires the exact key set from the plan (`test_fetcher.py:106-120`). `source=` is only `gdelt | news_rss | reddit | rss`. `market` is hardcoded `IN`. `signal_id` is `sha256(url)` so dedupe and primary key agree. A “simpler” `{title, link}` JSON would have broken Task 4 and the production port.

### Why `Decision.reason` is still required (and unused here)

Fetcher does not write decisions. The type lock stays so Task 10 cannot “temporarily” allow empty reasons. No change, on purpose.

### Why GDELT + Google News RSS + Reddit `.json` — and why TikTok / Meta were refused

These three are the plan’s free allowlist, character-for-character:

| Pipe | URL / query as locked | What it is for |
|---|---|---|
| GDELT 2.1 | `https://api.gdeltproject.org/api/v2/doc/doc` `query=neutrogena OR skincare` `mode=ArtList` `maxrecords=20` `format=json` | News / recalls graph. Spec already named GDELT as the cheap news pipe. |
| Google News RSS | `https://news.google.com/rss/search?q=skincare+OR+neutrogena&hl=en-IN` | India English news, no key. `hl=en-IN` is the market default. |
| Reddit `.json` | `https://www.reddit.com/r/SkincareAddiction/hot.json?limit=15` and `r/IndianSkincareAddicts` | Culture / vernacular-adjacent conversation without a Brandwatch contract. |
| Extra RSS | `fixtures/sources.yml` `rss: []` | Allowlist only. No “search the whole web.” |

TikTok and Meta are not “we did not get to them.” They are refused:

- Plan: “Sources (no scrape of TikTok/Meta).”
- Spec forbidden: TikTok Top Ads scrape; Meta Content Library (research-only, not commercial); Douyin as a TikTok proxy.
- Production may wrap **official** TikTok Discovery / Creative Center. That is a vendor adapter on the same `TrendSource` port, not a scrape in this commit.
- `test_default_sources_are_free_allowlist` asserts `brandwatch` / `firecrawl` / `tiktok` are **absent**.

Reddit sends `User-Agent: ContentMachineDemo/0.1` (`adapters/common.py:11, 34-35`; `test_reddit_sends_identifying_user_agent`). Anonymous default UA is how `.json` gets 403 even more often; an identifying UA is the minimum polite client. It did **not** clear the 403 on this LAN.

### Why a dead source continues

`run_fetch` (`boxes/fetcher.py:60-64`):

```python
for source in srcs:
    try:
        collected.extend(source.fetch(query_id))
    except Exception as exc:
        logger.warning("%s failed: %s", source.name, exc)
```

This is the spec’s scheduler rule in ten lines. One pipe’s exception is a warning, not a 500. Reddit additionally continues **inside** the adapter: one subreddit 403 does not drop the other (`reddit_json.py:33-41`; `test_one_reddit_403_does_not_drop_the_other`). Only “both feeds dead and no signals” raises, which `run_fetch` then logs.

We do not invent rows to replace a dead pipe. Empty-from-GDELT plus 20-from-News is the honest shelf.

### Why GDELT HTTP 200 `error` is a dead source

GDELT will answer **200** with `{"error": "query too broad"}`, an empty body, or JSON that has no `articles` key. The first adapter treated “no list” as “no news”:

```python
# 2c817fa — rejected in review
raw = payload.get("articles") or []
```

That is a silent fill-in. The spec’s lawyer sentence is “a failed source did not silently invent rows” — inventing *zero successful rows while claiming success* is the same lie in the opposite direction.

`7da5c99` (`adapters/gdelt.py:21-35, 57-58`):

- empty body → `RuntimeError`
- `{"error": "..."}` → `RuntimeError("GDELT error: …")`
- missing / non-list `articles` → `RuntimeError`
- `{"articles": []}` → success, zero signals (the list was present)
- a bare JSON list → treated as articles (GDELT sometimes does this)

`run_fetch` already turns that raise into “log and continue.” Tests: `test_gdelt_200_error_json_is_dead_source`, `test_gdelt_200_missing_article_list_is_dead_source`.

### Why in-process 6/60s rate limit instead of auth

Review Important: `POST /radar/fetch` was uncapped. A refresh loop is how you turn “GDELT 429 on this LAN” into “GDELT 429 for everyone we share an egress with.”

Fix (`apps/api/main.py:12-30, 47-55`):

- 6 hits / 60 seconds / `request.client.host`
- 7th → HTTP 429 `{"error": "Too many fetches. Please wait a minute and try again."}`
- no stack, no trace (asserted)
- `GET /health` is not limited (compose proof and load balancers stay green)
- `reset_rate_limit()` for tests; autouse fixture so tests do not poison each other
- per-host window: host `2.2.2.2` is not blocked when `1.1.1.1` is (`test_allow_radar_fetch_window`)

Auth was offered as the “grown-up” alternative and refused in the same fix round: no login, no other boxes. Production can put a real gateway in front of the same route. The demo needs a seatbelt, not an identity product.

### Why pages are never stored as prompts

Three layers, because one comment is not a defense:

1. **Do not keep the body.** `news_rss.py:78-79`: snippet is `summary` or `description`. Comment in code: “Never keep content:encoded / full HTML.”
2. **Strip and cap.** `clip_text` (`adapters/common.py:46-50`) unescapes, drops tags, caps at 500 chars. `raw_ref` is capped at 200 (`common.py:123`). GDELT snippet is `title (domain)`, not article text. Reddit snippet is `selftext` clipped, not the linked article.
3. **Test plants a landmine.** The mock RSS includes `content:encoded` = `FULL PAGE NEVER STORE THIS AS A PROMPT`. `_assert_signal_shape` fails if that string, `<html>`, or `<body>` appears in title/snippet/url/`raw_ref`.

`sources.yml` repeats the rule in a comment a human will read before adding a feed. Google News items stay `news.google.com/rss/articles/...` redirects; we do not scrape the publisher (task-3-report concern 3: ToS + injection). Task 5 may GET a *chosen* URL later, wrap the body in a data tag, and throw it away after the report. That is a different box.

### Why the API image now copies the whole tree, and dockerignore grew

Task 1’s `COPY main.py .` would have shipped a container that still only had `/health`. `2c817fa` changed the Dockerfile to `COPY . .`. That made `.dockerignore` load-bearing: without it, a local `.env` or `data/demo.db` would be baked into the image. Review Important #2. `7da5c99` adds `.env`, `.env.*`, `data/`, `*.db` next to the existing `.venv` / tests ignore. Runtime path is still the compose volume, not the image.

### Why `ports.py` only had `TrendSource`

The plan file map lists `ChatModel` and `ImageGen` in the same `ports.py`. The task-3 report: “ChatModel / ImageGen left for later tasks, as instructed.” A fetcher that imported an image port would have been scope creep. `ChatModel` arrived with the scorer. `ImageGen` is Task 9.

## 8. What we refused

- Brandwatch, Meltwater, Wizikey, Konnect, Firecrawl paid, Recraft.
- TikTok scrape, Meta Content Library, Douyin proxy, unofficial `old.reddit.com`.
- Auth / users / API keys on Fetch.
- Retry storms on GDELT 429.
- Treating GDELT 200-error as success (after review).
- Storing full pages or `content:encoded` as prompt text.
- Failing the whole Fetch when one pipe dies.
- Scorer, researcher, Command Center pages, CrewAI “research crew.”
- Committing `.env`, `.venv`, `data/*.db`, `.superpowers`.

## 9. Verification that actually ran

### Seen — mocked pytest at `2c817fa`

```text
.\.venv\Scripts\python.exe -m pytest tests/ -q
................                                                         [100%]
16 passed in 0.63s
```

| Test | Asserts |
|---|---|
| `test_gdelt_json_maps_to_signal` | ArtList JSON → Signal, UTC `seendate`, `source=gdelt` |
| `test_reddit_json_maps_to_signal` | permalink URL, `t3_` raw_ref (at this commit), snippet from selftext |
| `test_reddit_sends_identifying_user_agent` | every Reddit request is `ContentMachineDemo/0.1` |
| `test_run_fetch_dedupes_by_url` | same URL from GDELT + RSS → one row |
| `test_dead_source_logs_and_continues` | GDELT 500 → warning; Reddit + news still returned |
| `test_one_reddit_403_does_not_drop_the_other` | one sub 403, the other maps |
| `test_run_fetch_persists_signals` | SQLite `signals` URLs match the returned list |
| `test_post_radar_fetch_returns_signal_list` | `POST /radar/fetch` → JSON list (`run_fetch` mocked) |
| `test_default_sources_are_free_allowlist` | gdelt / news_rss / reddit present; brandwatch / firecrawl / tiktok absent |
| existing health + model tests | still green (7) |

Claimed TDD: 9 failing import tests first, then adapters. The red run is claimed in the report; the 16-pass run is seen.

### Seen — live `POST /radar/fetch` on 2026-08-19 (network up)

`TestClient(app).post("/radar/fetch")` → **200**, **≥1 real signal**.

| Source | Live result on this LAN |
|---|---|
| Google News RSS | **20 signals** (capped to GDELT’s `maxrecords=20`), `market=IN` |
| GDELT | **429** Too Many Requests — logged, others continued |
| Reddit both subs | **403** Blocked — logged, others continued |

Sample titles: Neutrogena boycott / skincare news via Google News. A second live `run_fetch(persist=False)` still returned 20 `news_rss` rows (RSS cap, not an empty cache).

This is the plan’s Step 3 bar: ≥1 real signal when the network is up. It is **not** “all three pipes healthy.”

### Seen — fix-round tests at `7da5c99`

First, expected red:

```text
pytest tests/test_fetcher.py::test_gdelt_200_error_json_is_dead_source \
       tests/test_fetcher.py::test_gdelt_200_missing_article_list_is_dead_source \
       tests/test_fetcher.py::test_radar_fetch_rate_limit \
       tests/test_fetcher.py::test_allow_radar_fetch_window
EEEE
# ImportError: cannot import name 'reset_rate_limit'
```

Then:

```text
.\.venv\Scripts\python.exe -m pytest tests/ -q
....................                                                     [100%]
20 passed in 0.58s
```

New tests: GDELT 200 `{"error":"query too broad"}` is a dead source; `{}` raises; 6×200 then 429; other host not blocked; health still `{"ok": true}`.

### Not seen in this task

A live GDELT 200 with articles, from this LAN, on 2026-08-19. A live Reddit 200, from this LAN, on 2026-08-19. Those pipes are implemented and mocked; they are not proven live here.

## 10. Review findings and rulings

Feature review on `074be52..2c817fa`: **not clean**. Three Important items. No Critical recorded.

| Severity | Finding | Ruling | Outcome |
|---|---|---|---|
| **Important** | GDELT HTTP 200 with `error` / empty / missing `articles` was treated as a successful empty fetch | 200 is not success unless an article list is present. Raise; `run_fetch` already continues. `{"articles": []}` stays a real empty. | **Fixed** in `7da5c99` (`gdelt.py` `_articles_or_fail`). Tests added. |
| **Important** | After `COPY . .`, `.dockerignore` did not exclude `.env` / `data/` / `*.db` | Bake must not copy secrets or the demo database. No runtime change. | **Fixed** in `7da5c99` (`apps/api/.dockerignore`). |
| **Important** | `POST /radar/fetch` uncapped | In-process 6/60s per client host. Friendly 429. No auth. Health unlimited. | **Fixed** in `7da5c99` (`main.py` limiter + tests). |
| **Minor (deferred)** | `radar_fetch` annotated `-> list[Signal]` but returns `JSONResponse` on 429 | Do not block. Type lie vs FastAPI’s “return a response.” | **Still open** (`apps/api/main.py:48-55`). Owner: production plan or a later typing pass. |
| LAN concern (not a code defect) | GDELT 429, Reddit 403, News works | Do not retry; do not add unofficial hosts. Dead source continues. | **Known**. See below. |

Fix review on `2c817fa..7da5c99`: ledger “3 addressed, 0 open” then **Task 3 complete, review clean**.

Exact reviewer prose beyond those bullets is **UNKNOWN** — not kept in the gitignored ledger.

## 11. Deferred / known holes

| Hole | Owner |
|---|---|
| **Known LAN behaviour (2026-08-19, this host):** GDELT **429**, Reddit both subs **403**, Google News **works** (20 rows). Fetch is still green. | Operator / later IP / production licensed listener. Not a code bug. Do not retry GDELT. Do not scrape `old.reddit.com`. |
| Google News links are `news.google.com/rss/articles/...` redirects, not publisher URLs | Task 5 may resolve a *chosen* URL under the researcher cap. Fetcher must not scrape the article. |
| `radar_fetch` return type vs `JSONResponse` 429 | production plan / typing pass |
| `ChatModel` / `ImageGen` not in `ports.py` at this commit | Tasks 4 and 9 |
| Reddit `raw_ref` later becomes JSON with `num_comments` | **Task 4** `f2f8059` (velocity). Do not treat today’s `reddit_json.py` as the Task 3 snapshot. |
| No schedule (“every 6 hours”) — Fetch is on-demand | production plan / Task 10 belt |
| Command Center Fetch button | **Task 11** |
| CI does not hit live GDELT | **Task 12** (pytest mocked is the gate) |
| `Signal.url == ""` still type-legal; adapters drop it | Task 2 minor, mitigated here |

## 12. Third-party check list

1. `git log --oneline 074be52..7da5c99` — two commits: `feat: free-source fetcher`, `fix: fetcher gdelt errors, dockerignore, rate limit`.
2. Open `docs/superpowers/plans/2026-08-19-demo.md:221-227` and `adapters/gdelt.py:17-51`, `news_rss.py:22-24`, `reddit_json.py:18-21`. The URLs and query strings must match the plan, not a “cleanup.”
3. `boxes/fetcher.py` `default_sources` is GDELT + News RSS + Reddit + extra YAML. `test_default_sources_are_free_allowlist` forbids `brandwatch` / `firecrawl` / `tiktok`.
4. `run_fetch` catches per-source exceptions and logs; it does not re-raise. `test_dead_source_logs_and_continues`.
5. `gdelt.py` `_articles_or_fail`: `{"error": "..."}` raises; `{}` raises; `{"articles": []}` does not. `test_gdelt_200_error_json_is_dead_source`.
6. `news_rss.py` does not read `content:encoded`. `test_fetcher.py` RSS fixture still contains `FULL PAGE NEVER STORE THIS AS A PROMPT`; `_assert_signal_shape` still bans it.
7. Reddit requests send `User-Agent: ContentMachineDemo/0.1`. One 403 does not drop the other sub.
8. `POST /radar/fetch`: six 200s, seventh 429 with a friendly `error` and no stack. `GET /health` still `{"ok": true}`.
9. `apps/api/Dockerfile` is `COPY . .`. `apps/api/.dockerignore` lists `.env`, `.env.*`, `data/`, `*.db`.
10. From `apps/api`: `pytest tests/test_fetcher.py tests/test_health.py tests/test_models.py` — green without network.
11. Optional live (network up): `POST /radar/fetch`. Expect ≥1 signal. On a residential LAN you may see GDELT 429 and Reddit 403 in the API log; News should still fill the list. That is the known behaviour, not a regression.
12. Confirm no Firecrawl client, no TikTok URL, no Meta Graph URL, no auth middleware in `main.py`.
