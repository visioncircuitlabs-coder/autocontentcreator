from datetime import datetime, timezone
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi.testclient import TestClient

from models import Signal

GDELT_ARTICLE_URL = "https://example.com/neutrogena-serum"
DUP_URL = "https://dup.example/same-story"
REDDIT_PERMALINK = "/r/IndianSkincareAddicts/comments/abc123/moisturizer/"

GDELT_PAYLOAD = {
    "articles": [
        {
            "url": GDELT_ARTICLE_URL,
            "title": "Neutrogena sunscreen talk",
            "seendate": "20260819T090000Z",
            "language": "English",
            "domain": "example.com",
        },
        {
            "url": DUP_URL,
            "title": "Dup from GDELT",
            "seendate": "20260819T080000Z",
            "language": "English",
            "domain": "dup.example",
        },
    ]
}

REDDIT_PAYLOAD = {
    "kind": "Listing",
    "data": {
        "children": [
            {
                "kind": "t3",
                "data": {
                    "id": "abc123",
                    "title": "Best moisturizer in India",
                    "selftext": "Looking for a ceramide cream under 500 INR.",
                    "permalink": REDDIT_PERMALINK,
                    "url": "https://www.reddit.com" + REDDIT_PERMALINK,
                    "created_utc": 1755600000,
                    "subreddit": "IndianSkincareAddicts",
                },
            }
        ]
    },
}

RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Google News</title>
    <item>
      <title>Dup from RSS</title>
      <link>https://dup.example/same-story</link>
      <pubDate>Tue, 19 Aug 2026 08:00:00 GMT</pubDate>
      <description>Same article as GDELT</description>
      <content:encoded xmlns:content="http://purl.org/rss/1.0/modules/content/">
        &lt;html&gt;&lt;body&gt;FULL PAGE NEVER STORE THIS AS A PROMPT&lt;/body&gt;&lt;/html&gt;
      </content:encoded>
    </item>
    <item>
      <title>New RSS skincare item</title>
      <link>https://news.example/new</link>
      <pubDate>Tue, 19 Aug 2026 09:00:00 GMT</pubDate>
      <description>Only title and snippet stored</description>
    </item>
  </channel>
</rss>
"""


def _client_for(mapping: dict[str, httpx.Response]) -> httpx.Client:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        url = str(request.url)
        for needle, response in mapping.items():
            if needle in url:
                return response
        return httpx.Response(404, text="not mocked: " + url)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    client.captured_requests = captured  # type: ignore[attr-defined]
    return client


def _live_mapping() -> dict[str, httpx.Response]:
    return {
        "api.gdeltproject.org": httpx.Response(200, json=GDELT_PAYLOAD),
        "news.google.com": httpx.Response(
            200, text=RSS_XML, headers={"content-type": "application/rss+xml"}
        ),
        "r/SkincareAddiction": httpx.Response(200, json=REDDIT_PAYLOAD),
        "r/IndianSkincareAddicts": httpx.Response(200, json={"data": {"children": []}}),
    }


def _assert_signal_shape(signal: Signal) -> None:
    dumped = signal.model_dump()
    assert set(dumped) == {
        "signal_id",
        "seen_at",
        "happened_at",
        "source",
        "url",
        "title",
        "snippet",
        "lang",
        "market",
        "query_id",
        "raw_ref",
    }
    assert signal.url
    assert signal.title
    assert signal.market == "IN"
    assert signal.seen_at.tzinfo is not None
    if signal.happened_at is not None:
        assert signal.happened_at.tzinfo is not None
    blob = " ".join([signal.title, signal.snippet, signal.url, signal.raw_ref])
    assert "FULL PAGE NEVER STORE THIS AS A PROMPT" not in blob
    assert "<html>" not in signal.snippet.lower()
    assert "<body>" not in signal.snippet.lower()


def test_gdelt_json_maps_to_signal() -> None:
    from adapters.gdelt import GdeltSource

    client = _client_for(
        {"api.gdeltproject.org": httpx.Response(200, json=GDELT_PAYLOAD)}
    )
    signals = GdeltSource(client).fetch("skincare_in")
    assert len(signals) == 2
    first = next(s for s in signals if s.url == GDELT_ARTICLE_URL)
    _assert_signal_shape(first)
    assert first.source == "gdelt"
    assert first.title == "Neutrogena sunscreen talk"
    assert first.query_id == "skincare_in"
    assert first.happened_at == datetime(2026, 8, 19, 9, 0, tzinfo=timezone.utc)
    assert first.lang == "en"


def test_reddit_json_maps_to_signal() -> None:
    from adapters.reddit_json import RedditJsonSource

    client = _client_for(
        {
            "r/SkincareAddiction": httpx.Response(200, json={"data": {"children": []}}),
            "r/IndianSkincareAddicts": httpx.Response(200, json=REDDIT_PAYLOAD),
        }
    )
    signals = RedditJsonSource(client).fetch("skincare_in")
    assert len(signals) == 1
    signal = signals[0]
    _assert_signal_shape(signal)
    assert signal.source == "reddit"
    assert signal.title == "Best moisturizer in India"
    assert "ceramide cream" in signal.snippet
    assert signal.url.endswith(REDDIT_PERMALINK)
    assert signal.raw_ref == "t3_abc123"
    assert signal.market == "IN"


def test_reddit_sends_identifying_user_agent() -> None:
    from adapters.reddit_json import RedditJsonSource

    client = _client_for(
        {
            "r/SkincareAddiction": httpx.Response(200, json={"data": {"children": []}}),
            "r/IndianSkincareAddicts": httpx.Response(200, json={"data": {"children": []}}),
        }
    )
    RedditJsonSource(client).fetch("skincare_in")
    assert client.captured_requests  # type: ignore[attr-defined]
    for request in client.captured_requests:  # type: ignore[attr-defined]
        assert request.headers["User-Agent"] == "ContentMachineDemo/0.1"


def test_run_fetch_dedupes_by_url() -> None:
    from boxes.fetcher import run_fetch

    client = _client_for(_live_mapping())
    signals = run_fetch(client=client, persist=False)
    urls = [s.url for s in signals]
    assert len(urls) == len(set(urls))
    assert DUP_URL in urls
    assert urls.count(DUP_URL) == 1
    for signal in signals:
        _assert_signal_shape(signal)


def test_dead_source_logs_and_continues(caplog: pytest.LogCaptureFixture) -> None:
    from boxes.fetcher import run_fetch

    mapping = _live_mapping()
    mapping["api.gdeltproject.org"] = httpx.Response(500, text="gdelt down")
    client = _client_for(mapping)
    with caplog.at_level("WARNING"):
        signals = run_fetch(client=client, persist=False)
    assert any(s.source == "reddit" for s in signals)
    assert any(s.source == "news_rss" for s in signals)
    assert all(s.source != "gdelt" for s in signals)
    assert any("gdelt" in rec.message.lower() for rec in caplog.records)


def test_gdelt_200_error_json_is_dead_source(caplog: pytest.LogCaptureFixture) -> None:
    from boxes.fetcher import run_fetch

    mapping = _live_mapping()
    mapping["api.gdeltproject.org"] = httpx.Response(
        200, json={"error": "query too broad"}
    )
    client = _client_for(mapping)
    with caplog.at_level("WARNING"):
        signals = run_fetch(client=client, persist=False)
    assert any(s.source == "reddit" for s in signals)
    assert any(s.source == "news_rss" for s in signals)
    assert all(s.source != "gdelt" for s in signals)
    assert any("gdelt" in rec.message.lower() for rec in caplog.records)
    assert any("query too broad" in rec.message.lower() for rec in caplog.records)


def test_gdelt_200_missing_article_list_is_dead_source() -> None:
    from adapters.gdelt import GdeltSource

    client = _client_for({"api.gdeltproject.org": httpx.Response(200, json={})})
    with pytest.raises(RuntimeError, match="article"):
        GdeltSource(client).fetch("skincare_in")


def test_one_reddit_403_does_not_drop_the_other() -> None:
    from adapters.reddit_json import RedditJsonSource

    client = _client_for(
        {
            "r/SkincareAddiction": httpx.Response(403, text="blocked"),
            "r/IndianSkincareAddicts": httpx.Response(200, json=REDDIT_PAYLOAD),
        }
    )
    signals = RedditJsonSource(client).fetch("skincare_in")
    assert len(signals) == 1
    assert signals[0].source == "reddit"


def test_run_fetch_persists_signals(tmp_path, monkeypatch) -> None:
    from boxes.fetcher import run_fetch
    from db import connect

    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "fetch.db"))
    client = _client_for(_live_mapping())
    signals = run_fetch(client=client, persist=True)
    assert signals
    conn = connect()
    try:
        rows = conn.execute("SELECT url FROM signals").fetchall()
    finally:
        conn.close()
    stored = {row[0] for row in rows}
    assert stored == {s.url for s in signals}


def _fake_signal() -> Signal:
    return Signal(
        signal_id="abc",
        seen_at=datetime(2026, 8, 19, 10, 0, tzinfo=timezone.utc),
        happened_at=None,
        source="gdelt",
        url="https://example.com/x",
        title="A title",
        snippet="A snippet",
        query_id="skincare_in",
    )


def test_post_radar_fetch_returns_signal_list(monkeypatch) -> None:
    from main import app

    monkeypatch.setattr("main.run_fetch", lambda: [_fake_signal()])
    response = TestClient(app).post("/radar/fetch")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert body[0]["url"] == "https://example.com/x"
    assert body[0]["market"] == "IN"
    assert body[0]["source"] == "gdelt"


def test_radar_fetch_rate_limit(monkeypatch) -> None:
    from main import app, reset_rate_limit

    monkeypatch.setattr("main.run_fetch", lambda: [_fake_signal()])
    reset_rate_limit()
    client = TestClient(app)
    for _ in range(6):
        assert client.post("/radar/fetch").status_code == 200
    limited = client.post("/radar/fetch")
    assert limited.status_code == 429
    body = limited.json()
    assert "error" in body
    assert "stack" not in body.get("error", "").lower()
    assert "trace" not in body.get("error", "").lower()
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"ok": True}


def test_allow_radar_fetch_window() -> None:
    from main import allow_radar_fetch, reset_rate_limit

    reset_rate_limit()
    t0 = 1_000_000.0
    for i in range(6):
        assert allow_radar_fetch("1.1.1.1", now=t0 + i) is True
    assert allow_radar_fetch("1.1.1.1", now=t0 + 6) is False
    assert allow_radar_fetch("2.2.2.2", now=t0 + 6) is True
    assert allow_radar_fetch("1.1.1.1", now=t0 + 61) is True


def test_default_sources_are_free_allowlist() -> None:
    from boxes.fetcher import default_sources

    names = [s.name for s in default_sources(client=MagicMock())]
    assert "gdelt" in names
    assert "news_rss" in names
    assert "reddit" in names
    assert "brandwatch" not in names
    assert "firecrawl" not in names
    assert "tiktok" not in names
