from conftest import client
from routers.test_user import create_user


def test_create_project(client):
    user_data = create_user(client)
    response = client.post(
        "/projects/projects/", json={
            "project_name": "Cisco",
            "project_description": "Cisco",
            "created_by_id": user_data["id"]
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["project_description"] == "Cisco"
    assert data["project_name"] == "Cisco"
    assert "updated_at" in data
    assert "created_at" in data
    assert "project_id" in data
    assert data["created_by_id"] == user_data["id"]
