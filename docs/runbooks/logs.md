# Logs

Local only. No keys.

- File: `data/logs/machine.jsonl` (Docker: `/data/logs/machine.jsonl`)
- Table: `events` in the same SQLite file as the demo
- Recent rows: http://localhost:3050/engine/events

Kinds you will see: `api_start`, `http`, `fetch_source`, `radar_start`, `radar_scored`, `radar_end`, `radar_fail`, `paint_start`, `paint_end`, `ui.look_click`, `ui.look_fail`, `ui.fetch_fail`.
