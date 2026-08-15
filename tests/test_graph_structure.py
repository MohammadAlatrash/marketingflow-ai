import pytest

from marketingflow.graph import (
    after_knowledge,
    after_strategy,
    after_supervisor,
    graph,
)


def test_graph_imports_and_has_expected_nodes():
    nodes = set(graph.get_graph().nodes)
    expected = {
        "supervisor",
        "client_knowledge",
        "research",
        "strategy",
        "content_creator",
        "novelty_gate",
        "reviewer",
        "knowledge_answer",
        "finalizer",
    }
    assert expected.issubset(nodes)


@pytest.mark.parametrize(
    ("route", "expected"),
    [
        ("knowledge_answer", "knowledge_answer"),
        ("content_only", "content_only"),
        ("strategy_only", "strategy_only"),
        ("full_campaign", "full_campaign"),
    ],
)
def test_after_supervisor_preserves_supported_route(route, expected):
    assert after_supervisor({"route": route}) == expected


def test_after_supervisor_defaults_to_full_campaign():
    assert after_supervisor({}) == "full_campaign"


@pytest.mark.parametrize(
    ("route", "expected"),
    [
        ("knowledge_answer", "knowledge_answer"),
        ("content_only", "content_creator"),
        ("strategy_only", "research"),
        ("full_campaign", "research"),
    ],
)
def test_after_knowledge_selects_expected_node(route, expected):
    assert after_knowledge({"route": route}) == expected


@pytest.mark.parametrize(
    ("route", "expected"),
    [
        ("strategy_only", "finalizer"),
        ("full_campaign", "content_creator"),
        ("content_only", "content_creator"),
    ],
)
def test_after_strategy_selects_expected_node(route, expected):
    assert after_strategy({"route": route}) == expected
