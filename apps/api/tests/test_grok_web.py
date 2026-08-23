import httpx
import pytest


def test_locked_query_is_india_skincare_not_open_web() -> None:
    from adapters.grok_web import LOCKED_QUERY

    lower = LOCKED_QUERY.lower()
    assert "india" in lower
    assert "skincare" in lower
    assert "search the whole web" not in lower


def test_items_from_citations_and_json() -> None:
    from adapters.grok_web import items_from_response

    rows = items_from_response(
        {
            "citations": ["https://www.vogue.in/beauty/a"],
            "output": [
                {
                    "content": [
                        {
                            "text": '{"items":[{"url":"https://www.vogue.in/beauty/a","title":"Night routine","snippet":"Double cleanse"}]}'
                        }
                    ]
                }
            ],
        }
    )
    assert rows
    assert rows[0]["url"] == "https://www.vogue.in/beauty/a"
    assert rows[0]["title"] == "Night routine"


def test_grok_web_without_key_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    from adapters.grok_web import GrokWebSource

    assert GrokWebSource().fetch("skincare_in") == []


def test_grok_web_fetch_builds_signals(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    from adapters.grok_web import GrokWebSource, XAI_RESPONSES

    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == XAI_RESPONSES
        raw = request.content.decode()
        assert "web_search" in raw
        assert "whole web" not in raw.lower()
        return httpx.Response(
            200,
            json={
                "citations": ["https://www.vogue.in/beauty/x"],
                "output": [
                    {
                        "content": [
                            {
                                "text": '{"items":[{"url":"https://www.vogue.in/beauty/x","title":"Double cleanse","snippet":"Night"}]}'
                            }
                        ]
                    }
                ],
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    rows = GrokWebSource(client).fetch("skincare_in")
    assert len(rows) == 1
    assert rows[0].source == "grok_web"
    assert "vogue.in" in rows[0].url
    assert "Double cleanse" in rows[0].title


def test_default_sources_include_grok_when_key_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import MagicMock

    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    from boxes.fetcher import default_sources

    names = [s.name for s in default_sources(client=MagicMock())]
    assert "grok_web" in names
    assert "brandwatch" not in names
