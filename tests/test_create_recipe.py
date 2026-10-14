import pytest

from framework.data import recipe_payload


def test_create_returns_the_stored_recipe(api, created_ids):
    payload = recipe_payload()

    response = api.create_recipe(payload)

    assert response.status_code == 201
    recipe = response.json()["recipe"]
    created_ids.append(recipe["id"])
    for field, value in payload.items():
        assert recipe[field] == value


def test_create_sets_location_header(api, created_ids):
    response = api.create_recipe(recipe_payload())

    recipe_id = response.json()["recipe"]["id"]
    created_ids.append(recipe_id)
    assert response.headers["Location"] == f"/recipes/{recipe_id}"


def test_create_assigns_unique_ids(make_recipe):
    first, second = make_recipe(), make_recipe()

    assert first["id"] != second["id"]


def test_new_recipe_has_equal_created_and_updated_timestamps(recipe):
    assert recipe["created_at"] == recipe["updated_at"]


@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"cost": 0}, id="zero-cost"),
        pytest.param({"title": "カレーライス"}, id="japanese-title"),
        pytest.param({"title": "x" * 200}, id="title-at-max-length"),
        pytest.param({"ingredients": "salt & pepper, 1/2 onion (diced)"}, id="punctuation"),
    ],
)
def test_create_accepts_boundary_values(make_recipe, overrides):
    recipe = make_recipe(**overrides)

    for field, value in overrides.items():
        assert recipe[field] == value
