import pytest

from framework.data import recipe_payload

pytestmark = pytest.mark.smoke


def test_service_is_healthy(api):
    response = api.health()

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recipe_lifecycle(api):
    """Create, read, update, delete: the main user flow end to end."""
    payload = recipe_payload()

    created = api.create_recipe(payload)
    assert created.status_code == 201
    recipe_id = created.json()["recipe"]["id"]

    fetched = api.get_recipe(recipe_id)
    assert fetched.status_code == 200
    assert fetched.json()["recipe"]["title"] == payload["title"]

    updated = api.update_recipe(recipe_id, {"cost": 1500})
    assert updated.status_code == 200
    assert updated.json()["recipe"]["cost"] == 1500

    assert api.delete_recipe(recipe_id).status_code == 204
    assert api.get_recipe(recipe_id).status_code == 404
