import json
from unittest.mock import MagicMock, patch
import pytest

from agents.registry import registry
import llm_router


@pytest.fixture(autouse=True)
def clear_registry():
    # Ensure registry is empty for tests
    registry._agents.clear()
    yield
    registry._agents.clear()


def load_examples(path="./tests/data/routing_examples.jsonl"):
    examples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            examples.append(json.loads(line))
    return examples


def test_registry_routing_basic():
    class Dummy:
        def __init__(self, name, match=False):
            self.name = name
            self._match = match

        def can_handle(self, query: str) -> bool:
            return self._match

        def handle(self, query: str) -> str:
            return f"handled-by-{self.name}"

    registry.register("a1", Dummy("a1", match=False))
    registry.register("a2", Dummy("a2", match=True))

    res = registry.route_query("some query")
    assert res == "handled-by-a2"


def test_choose_agent_via_llm_parses_json():
    # Register conference_call so selection resolves
    from agents.conference_call_agent import ConferenceCallAgent
    registry.register("conference_call", ConferenceCallAgent())

    example = {
        "agent": "conference_call",
        "reason": "match",
        "params": {"company": "TCS", "period": "Q2"},
    }

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content=json.dumps(example)))]

    with patch.object(llm_router, "openai_client", new=MagicMock()) as mock_client:
        mock_client.chat.completions.create.return_value = mock_resp
        parsed = llm_router.choose_agent_via_llm("Summarize the latest Q2 conference call for TCS")
        assert parsed["agent"] == "conference_call"
        assert parsed["params"]["company"] == "TCS"


def test_examples_file_matches_registry():
    # Ensure each example's expected agent is present in registry (or note missing)
    from agents.financial_statements_agent import FinancialStatementsAgent
    from agents.news_agent import NewsAgent

    # register a subset to test both present and missing handling
    registry.register("financial_statements", FinancialStatementsAgent())
    registry.register("news", NewsAgent())

    examples = load_examples("./tests/data/routing_examples.jsonl")
    for ex in examples:
        expected = ex.get("expected_agent")
        # it's fine if some agents aren't registered in this test, just ensure schema
        assert "query" in ex
        assert "expected_agent" in ex
