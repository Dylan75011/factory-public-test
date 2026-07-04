# Factory Public Test

A tiny public repository for testing Factory workflows.

This repo is intentionally small so an AI coding agent can quickly:

- inspect the codebase
- make a safe code change
- add or update tests
- run verification
- start a small management system
- prepare a pull request

## Quick Start

Run the test suite:

```bash
python3 -m unittest discover -s tests
```

Start the demo management system:

```bash
PYTHONPATH=src python3 -m factory_public_test.webapp --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

Try a simple change:

- Add a new task status such as `blocked`.
- Update the task summary output.
- Add a new unit test for the behavior.
- Add a task filter to the management system.

## Project Layout

```text
src/factory_public_test/  Python package
src/factory_public_test/static/  Browser UI for the management system
tests/                    Unit tests
```
