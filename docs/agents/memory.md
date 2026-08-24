# Brand Memory — how the machine gets smarter every time you say yes or no

**What this is:** every approve/reject decision becomes permanent brand memory,
stored twice — SQLite for the machine, Markdown for humans. You can open the
files, read what the system has learned, edit them by hand, and your edits
flow straight back into how captions get written.

## The one-paragraph version

When you approve or reject a post, three things happen: the decision lands in
the ledger (as before), it is mirrored into `data/memory/LEDGER.md`, and the
summary files are re-rendered. One of those files — `lessons.md` — belongs to
you. Write rules in it like *"never open with weather"* and the writer obeys
them from the next run onward. This is the Palantir idea (decisions are
first-class business objects, not log dust) combined with Anthropic's Claude
memory-tool idea (knowledge lives in files people can actually open).

## The files

```text
data/memory/
  LEDGER.md          every yes/no, human-readable, append-only
  winners.md         best-approved captions, ranked by win rate (machine)
  anti-patterns.md   most common rejection reasons        (machine)
  bans.md            twice-rejected captions, never regenerated (machine)
  lessons.md         YOUR FILE — rules the writer must follow
```

Files marked *(machine)* regenerate from the database any time — edit them and
your edit gets overwritten on the next rebuild. Only `lessons.md` survives
rebuilds.

## Editing lessons.md

```markdown
### les_007
- status: active
- scope: global
- rule: Open with the skin moment, never with the brand name.
- source: standing rule, demo fixture
```

- Add a new block with a new `les_XXX` id; set `status: retired` to retire one.
- `scope`: `global` or a SKU name.
- Blocks the parser cannot understand are skipped silently — generation never
  breaks because of a typo.
- Active lessons ride into every caption-writing prompt inside `<lessons>`.

## Where each idea came from

| Idea | Borrowed from |
|---|---|
| Decisions as first-class objects with links | [Palantir Foundry Ontology](https://www.palantir.com/docs/foundry/ontology/overview/) |
| Memory as editable files, not blobs | [Anthropic Claude memory tool](https://docs.claude.com/en/docs/agents-and-tools/tool-use/memory-tool) |
| Recurring rejects graduate into standing rules | [Cursor Project Rules + Memories](https://cursor.com/docs/context/rules) |
| Production feedback becoming eval material | [LangSmith datasets from runs](https://docs.langchain.com/langsmith/manage-datasets) |
| One store serving live inference + human review | [Feast offline/online stores](https://docs.feast.dev/getting-started/components/offline-store) · [Uber Michelangelo](https://www.uber.com/us/en/blog/michelangelo-machine-learning-platform/) |
| Snapshot memory before auto-updates so bad compounding is revertible | [Replit Checkpoints](https://docs.replit.com/references/version-control/checkpoints-and-rollbacks) |

Full industry survey with 17 verified sources: delegation report 2026-08-24
(also covers Braintrust log→experiment storage, OpenAI Evals over stored
completions, Langfuse annotation queues, Salesforce Atlas Agent Graph,
Databricks lineage, Block/Cash App online feature store, Snowflake Cortex
evals, Google ADK MemoryService, Duolingo Birdbrain, Netflix Metaflow,
Shopify Sidekick ground-truth sets).

## Ops

- `POST /memory/rebuild` (admin key required) — re-renders all five files from
  the database. Never touches your `lessons.md`.
- Memory writes never block an approval: if the disk fails, the yes/no still
  lands and a `memory_mirror_fail` event hits the log.
