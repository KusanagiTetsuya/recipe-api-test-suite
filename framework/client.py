"""Thin HTTP client for the Recipe API.

Tests call these methods instead of building URLs themselves, so a change to a
path or a header is made in one place.
"""

from __future__ import annotations

import requests

DEFAULT_TIMEOUT = 5  # seconds; a hung request should fail the test, not block CI


class RecipeApiClient:
    def __init__(self, base_url: str, timeout: float = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, f"{self.base_url}{path}", **kwargs)

    def health(self) -> requests.Response:
        return self.request("GET", "/health")

    def list_recipes(self) -> requests.Response:
        return self.request("GET", "/recipes")

    def create_recipe(self, payload) -> requests.Response:
        return self.request("POST", "/recipes", json=payload)

    def get_recipe(self, recipe_id) -> requests.Response:
        return self.request("GET", f"/recipes/{recipe_id}")

    def update_recipe(self, recipe_id, payload) -> requests.Response:
        return self.request("PATCH", f"/recipes/{recipe_id}", json=payload)

    def delete_recipe(self, recipe_id) -> requests.Response:
        return self.request("DELETE", f"/recipes/{recipe_id}")

    def close(self) -> None:
        self.session.close()
