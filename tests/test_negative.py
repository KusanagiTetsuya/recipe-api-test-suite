import pytest

from framework.data import recipe_payload, without

pytestmark = pytest.mark.negative

UNKNOWN_ID = 999_999_999
REQUIRED_FIELDS = ["title", "making_time", "serves", "ingredients", "cost"]

INVALID_VALUES = [
    pytest.param("title", "", id="empty-title"),
    pytest.param("title", "   ", id="blank-title"),
    pytest.param("title", 123, id="numeric-title"),
    pytest.param("title", None, id="null-title"),
    pytest.param("title", "x" * 201, id="title-over-max-length"),
    pytest.param("ingredients", ["onion"], id="ingredients-as-list"),
    pytest.param("cost", -1, id="negative-cost"),
    pytest.param("cost", "1000", id="cost-as-string"),
    pytest.param("cost", 9.99, id="fractional-cost"),
    pytest.param("cost", True, id="boolean-cost"),
]


def error_of(response) -> dict:
    return response.json()["error"]


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_create_rejects_missing_required_field(api, field):
    response = api.create_recipe(without(recipe_payload(), field))

    assert response.status_code == 400
    assert error_of(response)["code"] == "missing_field"
    assert error_of(response)["fields"] == [field]


def test_create_reports_every_missing_field(api):
    response = api.create_recipe({"title": "Only a title"})

    assert response.status_code == 400
    assert error_of(response)["fields"] == sorted(set(REQUIRED_FIELDS) - {"title"})


@pytest.mark.parametrize("field, value", INVALID_VALUES)
def test_create_rejects_invalid_value(api, field, value):
    response = api.create_recipe(recipe_payload(**{field: value}))

    assert response.status_code == 400
    assert error_of(response)["code"] == "invalid_value"
    assert error_of(response)["fields"] == [field]


@pytest.mark.parametrize("field, value", INVALID_VALUES)
def test_update_rejects_invalid_value_and_keeps_recipe(api, recipe, field, value):
    response = api.update_recipe(recipe["id"], {field: value})

    assert response.status_code == 400
    assert error_of(response)["code"] == "invalid_value"
    assert api.get_recipe(recipe["id"]).json()["recipe"] == recipe


def test_rejected_create_does_not_store_anything(api):
    title = recipe_payload()["title"]

    api.create_recipe(recipe_payload(title=title, cost=-1))

    titles = [item["title"] for item in api.list_recipes().json()["recipes"]]
    assert title not in titles


def test_create_rejects_unknown_field(api):
    response = api.create_recipe(recipe_payload(id=42))

    assert response.status_code == 400
    assert error_of(response)["code"] == "unknown_field"
    assert error_of(response)["fields"] == ["id"]


def test_update_rejects_empty_body(api, recipe):
    response = api.update_recipe(recipe["id"], {})

    assert response.status_code == 400
    assert error_of(response)["code"] == "missing_field"


@pytest.mark.parametrize(
    "kwargs",
    [
        pytest.param({"data": "{not json", "headers": {"Content-Type": "application/json"}}, id="malformed-json"),
        pytest.param({"json": ["a", "list"]}, id="json-array"),
        pytest.param({"data": "title=Curry"}, id="form-encoded"),
        pytest.param({}, id="no-body"),
    ],
)
def test_create_rejects_body_that_is_not_a_json_object(api, kwargs):
    response = api.request("POST", "/recipes", **kwargs)

    assert response.status_code == 400
    assert error_of(response)["code"] == "invalid_json"


@pytest.mark.parametrize("method", ["GET", "PATCH", "DELETE"])
def test_unknown_id_returns_not_found(api, method):
    kwargs = {"json": {"cost": 1}} if method == "PATCH" else {}

    response = api.request(method, f"/recipes/{UNKNOWN_ID}", **kwargs)

    assert response.status_code == 404
    assert error_of(response)["code"] == "not_found"


@pytest.mark.parametrize("recipe_id", ["abc", "1.5", "-1", "1e3"])
def test_non_numeric_id_returns_not_found(api, recipe_id):
    assert api.get_recipe(recipe_id).status_code == 404


@pytest.mark.parametrize(
    "method, path",
    [("PUT", "/recipes"), ("DELETE", "/recipes"), ("POST", "/recipes/1"), ("POST", "/health")],
)
def test_unsupported_method_returns_405(api, method, path):
    response = api.request(method, path)

    assert response.status_code == 405
    assert error_of(response)["code"] == "method_not_allowed"
