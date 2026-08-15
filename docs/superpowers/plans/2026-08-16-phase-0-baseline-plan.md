# Phase 0 implementation plan — baseline protection

Date: 2026-08-16

Design source: `../specs/2026-08-16-marketingflow-v3-upgrade-design.md`

## Objective

Protect the currently working V2 behavior before adding authentication or persistence. This phase must not make live Gemini calls during tests and must not change the visible campaign workflow.

## Definition of done

- The package, graph, Streamlit entry point, and CLI entry point import without a network call.
- Graph structure and all deterministic route functions are covered by tests.
- Configuration is read through one module and missing credentials produce a stable, non-secret error.
- The CLI no longer starts a paid workflow merely because its module is imported.
- The complete offline test suite passes in the project virtual environment.

## Tasks

### 1. Add reproducible test configuration

Files:

- Modify `pyproject.toml`.

Changes:

- Add a `dev` optional dependency containing pytest.
- Add pytest discovery/options for `tests/`.
- Do not add another runtime service or application dependency.

Verification:

```bash
.venv/bin/python -m pytest --collect-only
```

### 2. Centralize runtime configuration

Files:

- Create `marketingflow/config.py`.
- Modify `marketingflow/llm.py`.
- Modify `app.py` only where it reads the Gemini credential.
- Create `tests/test_config.py`.

Changes:

- Define an immutable settings object for the API key, generation model, and embedding model.
- Keep the existing environment variable names and model defaults in this phase.
- Allow tests to skip `.env` loading so the developer's real secret is never read or replaced.
- Raise a purpose-specific configuration exception without exposing a credential value.

Verification:

```bash
.venv/bin/python -m pytest tests/test_config.py
```

### 3. Make the CLI safe to import

Files:

- Modify `run_cli.py`.
- Create `tests/test_entrypoints.py`.

Changes:

- Move demo state creation into a small function.
- Invoke the live graph only from `main()`.
- Keep direct `python run_cli.py` behavior unchanged.
- Prove that importing the module does not invoke the graph.

Verification:

```bash
.venv/bin/python -m pytest tests/test_entrypoints.py
```

### 4. Expand graph baseline tests

Files:

- Modify `tests/test_graph_structure.py`.

Changes:

- Assert required nodes and graph entry behavior.
- Unit-test `after_supervisor`, `after_knowledge`, and `after_strategy` for every supported deterministic route.
- Do not patch or call Gemini.

Verification:

```bash
.venv/bin/python -m pytest tests/test_graph_structure.py
```

### 5. Run the local baseline gate

Commands:

```bash
.venv/bin/python -m compileall -q marketingflow app.py run_cli.py tests
.venv/bin/python -m pytest
.venv/bin/python -c "import marketingflow.graph; import run_cli"
```

Then start Streamlit headlessly on a temporary local port, verify its health endpoint, and stop it. No generation button is submitted, so no Gemini call occurs.

## Out of scope

- Supabase packages, migrations, Auth UI, or credentials.
- Persistent tables or Storage.
- Prompt or graph behavior changes.
- UI redesign.
- Live Gemini generation tests.

## Rollback boundary

All Phase 0 changes are isolated on `upgrade/v3-foundation` and will be committed separately from the design checkpoint. The existing `main` branch remains untouched.
