import pytest


@pytest.mark.parametrize(
    "field, value",
    [
        ("title", "Tomato Soup"),
        ("making_time", "15 min"),
        ("serves", "5 people"),
        ("ingredients", "onion, tomato, seasoning, water"),
        ("cost", 450),
    ],
)
def test_update_changes_only_the_given_field(api, recipe, field, value):
    response = api.update_recipe(recipe["id"], {field: value})

    assert response.status_code == 200
    updated = response.json()["recipe"]
    assert updated[field] == value
    untouched = set(recipe) - {field, "updated_at"}
    assert {name: updated[name] for name in untouched} == {name: recipe[name] for name in untouched}


def test_update_is_persisted(api, recipe):
    api.update_recipe(recipe["id"], {"title": "Tomato Soup", "cost": 450})

    stored = api.get_recipe(recipe["id"]).json()["recipe"]

    assert (stored["title"], stored["cost"]) == ("Tomato Soup", 450)


def test_update_keeps_created_at_and_advances_updated_at(api, recipe):
    updated = api.update_recipe(recipe["id"], {"cost": 1}).json()["recipe"]

    assert updated["created_at"] == recipe["created_at"]
    assert updated["updated_at"] >= recipe["updated_at"]
