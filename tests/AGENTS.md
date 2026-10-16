# Test conventions

Tests live in `tests/`. Repo-wide setup and commands are in the root
`AGENTS.md`.

- Run all tests: `just test` (or `uv run pytest tests`). Postgres must be
  running (`just db-start`); pytest-django creates `test_puka`.
- Bare `uv run pytest` collects nothing: `testpaths = ["puka"]` in
  `pyproject.toml`, but tests live in `tests/` (`*_test.py`).
- Single test: `uv run pytest tests/stuff/item_model_test.py::test_name`.
- Coverage: `just coverage`.
- Layout: `tests/` mirrors the apps; `tests/conftest.py` holds fixtures
  and `tests/factories.py` factories (factory_boy, registered via
  pytest-factoryboy).
- DB tests need `@pytest.mark.django_db` or the `db` fixture.
