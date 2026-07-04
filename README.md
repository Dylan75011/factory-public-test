# Factory Public Test

A tiny public repository for testing Factory workflows.

This repo is intentionally small so an AI coding agent can quickly:

- inspect the codebase
- make a safe code change
- add or update tests
- run verification
- prepare a pull request

## Quick Start

Run the test suite:

```bash
python3 -m unittest discover -s tests
```

Try a simple change:

- Add a new task status such as `blocked`.
- Update the task summary output.
- Add a new unit test for the behavior.

## Project Layout

```text
src/factory_public_test/  Python package
tests/                    Unit tests
.github/workflows/        CI workflow
```

