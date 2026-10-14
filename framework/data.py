"""Test data builders."""

from __future__ import annotations

import uuid


def recipe_payload(**overrides) -> dict:
    """A valid recipe body. Titles are unique so tests never collide."""
    payload = {
        "title": f"Chicken Curry {uuid.uuid4().hex[:8]}",
        "making_time": "45 min",
        "serves": "4 people",
        "ingredients": "onion, chicken, seasoning",
        "cost": 1000,
    }
    payload.update(overrides)
    return payload


def without(payload: dict, field: str) -> dict:
    return {key: value for key, value in payload.items() if key != field}
