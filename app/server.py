"""Recipe API: the system under test.

A small in-memory REST service. It exists so the test suite has a real HTTP
target that starts in milliseconds and needs no database, which keeps CI fast
and deterministic.
"""

from __future__ import annotations

import itertools
import threading
from datetime import datetime, timezone

from flask import Flask, jsonify, request

TEXT_FIELDS = ("title", "making_time", "serves", "ingredients")
FIELDS = TEXT_FIELDS + ("cost",)
MAX_TEXT_LENGTH = 200


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _error(status: int, code: str, message: str, fields: list[str] | None = None):
    body = {"error": {"code": code, "message": message}}
    if fields:
        body["error"]["fields"] = sorted(fields)
    return jsonify(body), status


def _invalid_fields(payload: dict) -> list[str]:
    """Return the names of fields in the payload that hold an invalid value."""
    bad = []
    for name, value in payload.items():
        if name in TEXT_FIELDS:
            ok = (
                isinstance(value, str)
                and value.strip() != ""
                and len(value) <= MAX_TEXT_LENGTH
            )
        else:  # cost
            ok = isinstance(value, int) and not isinstance(value, bool) and value >= 0
        if not ok:
            bad.append(name)
    return bad


def create_app() -> Flask:
    app = Flask(__name__)
    recipes: dict[int, dict] = {}
    next_id = itertools.count(1)
    lock = threading.Lock()

    def read_payload():
        """Parse the JSON body. Returns (payload, error_response)."""
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return None, _error(400, "invalid_json", "Request body must be a JSON object.")
        unknown = [name for name in payload if name not in FIELDS]
        if unknown:
            return None, _error(400, "unknown_field", "Unknown field in request body.", unknown)
        return payload, None

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/recipes")
    def list_recipes():
        with lock:
            items = [recipes[key] for key in sorted(recipes)]
        return jsonify({"recipes": items})

    @app.post("/recipes")
    def create_recipe():
        payload, error = read_payload()
        if error:
            return error
        missing = [name for name in FIELDS if name not in payload]
        if missing:
            return _error(400, "missing_field", "Required field is missing.", missing)
        invalid = _invalid_fields(payload)
        if invalid:
            return _error(400, "invalid_value", "Field has an invalid value.", invalid)

        timestamp = _now()
        with lock:
            recipe_id = next(next_id)
            recipe = {"id": recipe_id, **payload, "created_at": timestamp, "updated_at": timestamp}
            recipes[recipe_id] = recipe
        response = jsonify({"recipe": recipe})
        response.status_code = 201
        response.headers["Location"] = f"/recipes/{recipe_id}"
        return response

    @app.get("/recipes/<int:recipe_id>")
    def get_recipe(recipe_id: int):
        with lock:
            recipe = recipes.get(recipe_id)
        if recipe is None:
            return _error(404, "not_found", "Recipe not found.")
        return jsonify({"recipe": recipe})

    @app.patch("/recipes/<int:recipe_id>")
    def update_recipe(recipe_id: int):
        payload, error = read_payload()
        if error:
            return error
        if not payload:
            return _error(400, "missing_field", "Provide at least one field to update.")
        invalid = _invalid_fields(payload)
        if invalid:
            return _error(400, "invalid_value", "Field has an invalid value.", invalid)
        with lock:
            recipe = recipes.get(recipe_id)
            if recipe is None:
                return _error(404, "not_found", "Recipe not found.")
            recipe = {**recipe, **payload, "updated_at": _now()}
            recipes[recipe_id] = recipe
        return jsonify({"recipe": recipe})

    @app.delete("/recipes/<int:recipe_id>")
    def delete_recipe(recipe_id: int):
        with lock:
            removed = recipes.pop(recipe_id, None)
        if removed is None:
            return _error(404, "not_found", "Recipe not found.")
        return "", 204

    @app.errorhandler(404)
    def not_found(_):
        return _error(404, "not_found", "Resource not found.")

    @app.errorhandler(405)
    def method_not_allowed(_):
        return _error(405, "method_not_allowed", "Method not allowed for this resource.")

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8000)
