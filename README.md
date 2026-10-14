# Recipe API Test Suite

[![tests](https://github.com/dbsants/recipe-api-test-suite/actions/workflows/tests.yml/badge.svg)](https://github.com/dbsants/recipe-api-test-suite/actions/workflows/tests.yml)

Automated API tests for a small recipe REST service, written in Python with
pytest and requests. The suite runs on every push in GitHub Actions and in a
single Docker command.

The repository contains both the tests and the service they exercise, so anyone
can clone it and see a green run in under a minute, with no database or
external account.

## What is covered

79 test cases across six areas:

| Area | File | Examples |
|---|---|---|
| Smoke | `tests/test_smoke.py` | health check, full create → read → update → delete flow |
| Create | `tests/test_create_recipe.py` | stored values, `Location` header, unique ids, boundary values |
| Read | `tests/test_read_recipes.py` | fetch by id, list contents and ordering |
| Update / Delete | `tests/test_update_recipe.py`, `tests/test_delete_recipe.py` | partial update leaves other fields untouched, delete is not repeatable |
| Contract | `tests/test_contract.py` | every success and error body is validated against a JSON Schema |
| Negative | `tests/test_negative.py` | missing fields, wrong types, malformed JSON, unknown ids, unsupported methods |

## Quick start

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
```

Useful variations:

```bash
pytest -m smoke                  # fast checks only
pytest -m "not negative"         # skip error-handling cases
pytest -k update -v              # tests whose name contains "update"
pytest --html=reports/report.html --self-contained-html
```

### Run against another environment

By default the suite starts the bundled service on a free local port. Set
`BASE_URL` to point the same tests at a deployment that is already running:

```bash
BASE_URL=http://localhost:8000 pytest
```

To start the bundled service by hand: `python -m app.server` (port 8000).

### Run in Docker

```bash
docker build -t recipe-api-tests .
docker run --rm -v "$PWD/reports:/suite/reports" recipe-api-tests
```

The HTML and JUnit reports are written to `reports/`.

## Project layout

```
app/server.py            the service under test (Flask, in-memory)
framework/client.py      HTTP client: one method per endpoint
framework/schemas.py     JSON Schemas for the API contract
framework/data.py        test data builders
tests/conftest.py        fixtures: server start-up, client, data clean-up
tests/test_*.py          test cases
.github/workflows/       CI pipeline
Dockerfile               containerised test run
```

## Design decisions

- **Tests go through real HTTP.** The service is started on a socket and called
  with `requests`, rather than through Flask's in-process test client. That is
  what makes the `BASE_URL` switch possible.
- **Each test owns its data.** Tests create the recipes they need through a
  factory fixture and the fixture deletes them afterwards, even when the test
  fails. No test relies on another test or on the starting state of the
  service, so they can run in any order and against a shared environment.
- **Client layer between tests and HTTP.** Tests call `api.create_recipe(...)`
  instead of building URLs. A changed path is fixed in one file.
- **Contract checked with JSON Schema.** Schemas use
  `additionalProperties: false`, so an unexpected new field fails the build
  instead of slipping through.
- **Negative cases are table-driven.** Invalid values live in one
  parametrised list that is reused for both create and update.
- **Failed writes are checked for side effects.** A rejected request must also
  leave the stored data unchanged, not only return 400.

## API under test

| Method | Path | Success | Errors |
|---|---|---|---|
| GET | `/health` | 200 | |
| GET | `/recipes` | 200 | |
| POST | `/recipes` | 201 + `Location` | 400 |
| GET | `/recipes/{id}` | 200 | 404 |
| PATCH | `/recipes/{id}` | 200 | 400, 404 |
| DELETE | `/recipes/{id}` | 204 | 404 |

A recipe has `title`, `making_time`, `serves`, `ingredients` (non-empty strings,
up to 200 characters) and `cost` (non-negative integer). Errors use one shape:

```json
{"error": {"code": "invalid_value", "message": "Field has an invalid value.", "fields": ["cost"]}}
```

## Continuous integration

`.github/workflows/tests.yml` runs the suite on Python 3.11, 3.12 and 3.13 for
every push to `main` and every pull request, and uploads the HTML report as a
build artifact.

## Roadmap

- [ ] Evaluation tests for an LLM-backed endpoint (rule checks and an LLM judge)
- [ ] UI checks with Playwright
- [ ] Run the suite against a MySQL-backed implementation of the same contract

## License

MIT
