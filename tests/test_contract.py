import pytest

from framework import schemas
from framework.data import recipe_payload

pytestmark = pytest.mark.contract

UNKNOWN_ID = 999_999_999


def test_create_response_matches_schema(api, created_ids):
    response = api.create_recipe(recipe_payload())
    created_ids.append(response.json()["recipe"]["id"])

    schemas.assert_matches(response.json(), schemas.RECIPE_RESPONSE)


def test_get_response_matches_schema(api, recipe):
    schemas.assert_matches(api.get_recipe(recipe["id"]).json(), schemas.RECIPE_RESPONSE)


def test_update_response_matches_schema(api, recipe):
    response = api.update_recipe(recipe["id"], {"cost": 1})

    schemas.assert_matches(response.json(), schemas.RECIPE_RESPONSE)


def test_list_response_matches_schema(api, recipe):
    schemas.assert_matches(api.list_recipes().json(), schemas.RECIPE_LIST_RESPONSE)


@pytest.mark.parametrize(
    "call",
    [
        pytest.param(lambda api: api.get_recipe(UNKNOWN_ID), id="not-found"),
        pytest.param(lambda api: api.create_recipe({}), id="validation"),
        pytest.param(lambda api: api.request("PUT", "/recipes"), id="method-not-allowed"),
        pytest.param(lambda api: api.request("GET", "/no-such-route"), id="unknown-route"),
    ],
)
def test_error_responses_match_schema(api, call):
    response = call(api)

    assert response.headers["Content-Type"].startswith("application/json")
    schemas.assert_matches(response.json(), schemas.ERROR_RESPONSE)


@pytest.mark.parametrize("path", ["/health", "/recipes"])
def test_success_responses_are_json(api, path):
    response = api.request("GET", path)

    assert response.headers["Content-Type"].startswith("application/json")
