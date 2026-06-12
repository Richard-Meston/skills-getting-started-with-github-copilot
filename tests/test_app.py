from fastapi.testclient import TestClient
import copy
import pytest
from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))


def test_get_activities_returns_all():
    # Arrange
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    assert resp.json() == app_module.activities


def test_signup_success():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    assert email not in app_module.activities[activity]["participants"]

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]
    assert "Signed up" in resp.json().get("message", "")


def test_signup_already_registered():
    # Arrange
    activity = "Chess Club"
    email = app_module.activities[activity]["participants"][0]

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student is already signed up for this activity"


def test_signup_activity_not_found():
    # Act
    resp = client.post("/activities/Unknown/signup", params={"email": "a@b.com"})

    # Assert
    assert resp.status_code == 404


def test_remove_participant_success():
    # Arrange
    activity = "Chess Club"
    email = app_module.activities[activity]["participants"][0]

    # Act
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email not in app_module.activities[activity]["participants"]


def test_remove_participant_not_found():
    # Arrange
    activity = "Chess Club"
    email = "notfound@mergington.edu"

    # Act
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Participant not found"


def test_remove_activity_not_found():
    # Act
    resp = client.delete("/activities/Unknown/participants", params={"email": "a@b.com"})

    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"
