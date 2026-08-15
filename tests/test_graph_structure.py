from marketingflow.graph import graph


def test_graph_imports_and_has_expected_nodes():
    nodes = set(graph.get_graph().nodes)
    expected = {
        "supervisor",
        "client_knowledge",
        "research",
        "strategy",
        "content_creator",
        "reviewer",
        "knowledge_answer",
        "finalizer",
    }
    assert expected.issubset(nodes)
