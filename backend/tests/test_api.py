import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.db.session import get_session


class FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return self._rows

    def first(self):
        return self._rows[0] if self._rows else None


class FakeSession:
    def __init__(self, rows, scalar_result=1):
        self._rows = rows
        self._scalar_result = scalar_result
        self.added_objects = []
        self._next_id = 1

    async def execute(self, _query):
        return FakeResult(self._rows)

    async def scalar(self, _query):
        return self._scalar_result

    def add(self, obj):
        self.added_objects.append(obj)

    async def commit(self):
        return None

    async def refresh(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = self._next_id
            self._next_id += 1


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_greens():
    polygon = json.dumps({"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]})
    rows = [
        type(
            "Row",
            (),
            {
                "id": 1,
                "name": "Park",
                "polygon": polygon,
                "frequency_days": 14,
                "last_mowed_at": datetime(2024, 1, 1, 12, 0, 0),
            },
        )()
    ]

    async def override_session():
        yield FakeSession(rows)

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)
    response = client.get("/api/v1/greens")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "Park",
            "polygon": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]},
            "frequency_days": 14,
            "last_mowed_at": "2024-01-01T12:00:00",
        }
    ]


def test_list_lamps():
    point = json.dumps({"type": "Point", "coordinates": [15.1, 49.2]})
    rows = [type("Row", (), {"id": 2, "name": "Lamp A", "point": point})()]

    async def override_session():
        yield FakeSession(rows)

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)
    response = client.get("/api/v1/lamps")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 2, "name": "Lamp A", "point": {"type": "Point", "coordinates": [15.1, 49.2]}}
    ]


def test_bins_list_and_detail():
    point = json.dumps({"type": "Point", "coordinates": [14.0, 50.0]})
    rows = [
        type(
            "Row",
            (),
            {
                "id": 3,
                "name": "Bin 1",
                "point": point,
                "last_fill_level": 75.5,
                "last_battery_level": 88.2,
                "last_temperature": 22.1,
                "updated_at": datetime(2024, 5, 1, 8, 30, 0),
            },
        )()
    ]

    async def override_session():
        yield FakeSession(rows)

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)

    list_response = client.get("/api/v1/bins")
    assert list_response.status_code == 200
    assert list_response.json() == [
        {
            "id": 3,
            "name": "Bin 1",
            "point": {"type": "Point", "coordinates": [14.0, 50.0]},
            "last_fill_level": 75.5,
            "last_battery_level": 88.2,
            "last_temperature": 22.1,
            "updated_at": "2024-05-01T08:30:00",
        }
    ]

    detail_response = client.get("/api/v1/bins/3")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == 3


def test_get_bin_not_found_returns_404():
    async def override_session():
        yield FakeSession([])

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)

    response = client.get("/api/v1/bins/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Bin not found"


def test_post_bin_telemetry_requires_token():
    settings.telemetry_api_tokens = "valid-token"

    async def override_session():
        yield FakeSession([])

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)

    response = client.post("/api/v1/bins/1/telemetry", json={"fill_level": 10})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API token"


def test_post_bin_telemetry_accepts_valid_token_and_persists():
    settings.telemetry_api_tokens = "valid-token"
    telemetry_rows = []

    async def override_session():
        yield FakeSession(telemetry_rows)

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)

    response = client.post(
        "/api/v1/bins/5/telemetry",
        json={"fill_level": 42.5, "battery_level": 95.0},
        headers={"X-API-TOKEN": "valid-token"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["bin_id"] == 5
    assert body["fill_level"] == 42.5
    assert body["battery_level"] == 95.0


def test_get_bin_telemetry_returns_entries():
    settings.telemetry_api_tokens = "valid-token"
    rows = [
        type(
            "Row",
            (),
            {
                "id": 1,
                "bin_id": 7,
                "fill_level": 10.0,
                "battery_level": 50.0,
                "temperature": 21.5,
                "at_time": datetime(2024, 6, 1, 12, 0, 0),
            },
        )(),
        type(
            "Row",
            (),
            {
                "id": 2,
                "bin_id": 7,
                "fill_level": None,
                "battery_level": None,
                "temperature": None,
                "at_time": datetime(2024, 6, 1, 13, 0, 0),
            },
        )(),
    ]

    async def override_session():
        yield FakeSession(rows)

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)

    response = client.get("/api/v1/bins/7/telemetry")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "bin_id": 7,
            "fill_level": 10.0,
            "battery_level": 50.0,
            "temperature": 21.5,
            "at_time": "2024-06-01T12:00:00",
        },
        {
            "id": 2,
            "bin_id": 7,
            "fill_level": None,
            "battery_level": None,
            "temperature": None,
            "at_time": "2024-06-01T13:00:00",
        },
    ]
