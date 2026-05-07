from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

INITIAL_ACTIVITIES = deepcopy(activities)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    activity_name = quote("Chess Club")
    email = "new.student@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={quote(email)}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    response = client.get("/activities")
    assert email in response.json()["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    activity_name = quote("Chess Club")
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={quote(email)}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_removes_participant():
    activity_name = quote("Chess Club")
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup?email={quote(email)}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"

    response = client.get("/activities")
    assert email not in response.json()["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404():
    activity_name = quote("Chess Club")
    email = "notfound@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup?email={quote(email)}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unregister_unknown_activity_returns_404():
    activity_name = quote("Unknown Club")
    email = "student@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup?email={quote(email)}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
