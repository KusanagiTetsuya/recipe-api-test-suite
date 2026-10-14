def test_delete_returns_no_content(api, make_recipe):
    recipe = make_recipe()

    response = api.delete_recipe(recipe["id"])

    assert response.status_code == 204
    assert response.content == b""


def test_deleted_recipe_cannot_be_fetched(api, recipe):
    api.delete_recipe(recipe["id"])

    assert api.get_recipe(recipe["id"]).status_code == 404


def test_delete_twice_returns_not_found(api, recipe):
    api.delete_recipe(recipe["id"])

    assert api.delete_recipe(recipe["id"]).status_code == 404


def test_delete_does_not_affect_other_recipes(api, make_recipe):
    kept, removed = make_recipe(), make_recipe()

    api.delete_recipe(removed["id"])

    assert api.get_recipe(kept["id"]).json()["recipe"] == kept
