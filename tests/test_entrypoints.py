import importlib
import runpy
import sys
from pathlib import Path
from unittest.mock import Mock

import marketingflow.config
from marketingflow.graph import graph


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_cli_import_does_not_invoke_graph(monkeypatch):
    invoke = Mock()
    monkeypatch.setattr(graph, "invoke", invoke)
    sys.modules.pop("run_cli", None)

    module = importlib.import_module("run_cli")

    invoke.assert_not_called()
    assert module.build_demo_state()["duration_days"] == 7


def test_streamlit_entrypoint_executes_without_network(monkeypatch):
    monkeypatch.setattr(marketingflow.config, "load_dotenv", Mock())
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setattr(graph, "invoke", Mock(side_effect=AssertionError("network path")))

    runpy.run_path(str(PROJECT_ROOT / "app.py"), run_name="streamlit_smoke_test")

    graph.invoke.assert_not_called()
