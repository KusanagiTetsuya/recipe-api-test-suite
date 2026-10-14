"""JSON Schemas for the Recipe API responses (the API contract)."""

from __future__ import annotations

from jsonschema import Draft202012Validator

RECIPE = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "id", "title", "making_time", "serves", "ingredients", "cost",
        "created_at", "updated_at",
    ],
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "title": {"type": "string", "minLength": 1},
        "making_time": {"type": "string", "minLength": 1},
        "serves": {"type": "string", "minLength": 1},
        "ingredients": {"type": "string", "minLength": 1},
        "cost": {"type": "integer", "minimum": 0},
        "created_at": {"type": "string", "minLength": 1},
        "updated_at": {"type": "string", "minLength": 1},
    },
}

RECIPE_RESPONSE = {
    "type": "object",
    "additionalProperties": False,
    "required": ["recipe"],
    "properties": {"recipe": RECIPE},
}

RECIPE_LIST_RESPONSE = {
    "type": "object",
    "additionalProperties": False,
    "required": ["recipes"],
    "properties": {"recipes": {"type": "array", "items": RECIPE}},
}

ERROR_RESPONSE = {
    "type": "object",
    "additionalProperties": False,
    "required": ["error"],
    "properties": {
        "error": {
            "type": "object",
            "additionalProperties": False,
            "required": ["code", "message"],
            "properties": {
                "code": {"type": "string", "minLength": 1},
                "message": {"type": "string", "minLength": 1},
                "fields": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            },
        }
    },
}


def assert_matches(body, schema) -> None:
    """Fail with every schema violation listed, not just the first one."""
    errors = sorted(Draft202012Validator(schema).iter_errors(body), key=lambda e: list(e.path))
    assert not errors, "Response does not match schema:\n" + "\n".join(
        f"  {'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors
    )
