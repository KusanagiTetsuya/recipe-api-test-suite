def test_get_returns_recipe_by_id(api, recipe):
    response = api.get_recipe(recipe["id"])

    assert response.status_code == 200
    assert response.json()["recipe"] == recipe


def test_list_contains_created_recipes(api, make_recipe):
    first, second = make_recipe(), make_recipe()

    response = api.list_recipes()

    assert response.status_code == 200
    listed = {item["id"]: item for item in response.json()["recipes"]}
    assert listed[first["id"]] == first
    assert listed[second["id"]] == second


def test_list_is_ordered_by_id(api, make_recipe):
    make_recipe(), make_recipe(), make_recipe()

    ids = [item["id"] for item in api.list_recipes().json()["recipes"]]

    assert ids == sorted(ids)


def test_deleted_recipe_is_not_listed(api, recipe):
    api.delete_recipe(recipe["id"])

    ids = [item["id"] for item in api.list_recipes().json()["recipes"]]

    assert recipe["id"] not in ids
