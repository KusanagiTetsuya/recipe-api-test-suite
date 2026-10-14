"""Shared fixtures.

By default the suite starts the bundled Recipe API on a free local port.
Set BASE_URL to run the same tests against an already running deployment:

    BASE_URL=https://staging.example.com pytest
"""

from __future__ import annotations

import os
import threading

import pytest
from werkzeug.serving import make_server

from app.server import create_app
from framework.client import RecipeApiClient
from framework.data import recipe_payload


@pytest.fixture(scope="session")
def base_url():
    external = os.environ.get("BASE_URL")
    if external:
        yield external
        return

    server = make_server("127.0.0.1", 0, create_app(), threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    thread.join(timeout=5)


@pytest.fixture(scope="session")
def api(base_url):
    client = RecipeApiClient(base_url)
    yield client
    client.close()


@pytest.fixture
def created_ids(api):
    """Collects recipe ids and deletes them after the test, pass or fail."""
    ids: list[int] = []
    yield ids
    for recipe_id in ids:
        api.delete_recipe(recipe_id)


@pytest.fixture
def make_recipe(api, created_ids):
    """Factory: create a recipe through the API and return its JSON."""

    def _make(**overrides) -> dict:
        response = api.create_recipe(recipe_payload(**overrides))
        assert response.status_code == 201, response.text
        recipe = response.json()["recipe"]
        created_ids.append(recipe["id"])
        return recipe

    return _make


@pytest.fixture
def recipe(make_recipe) -> dict:
    return make_recipe()
