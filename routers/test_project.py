from faker import Faker

from conftest import client
from routers.test_user import create_user

fake = Faker()


def create_project(client, access_token_fixture):
    access_token = access_token_fixture
    user_data = create_user(client)
    breakpoint()
    response = client.post(
        "/projects/projects/", json={
            "project_name": fake.company(),  # Generate a random company name as the project name
            "project_description": fake.text(),  # Generate a random text as the project description
            "created_by_id": user_data['id']  # Generate a random integer as the created_by_id
        }, headers={"Authorization": f"bearer {access_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    return data


# def test_create_project(client, access_token_fixture):
#     access_token = access_token_fixture
#     user_data = create_user(client)
#     data = create_project(client, access_token)
#     assert "project_description" in data
#     assert "project_name" in data
#     assert "updated_at" in data
#     assert "created_at" in data
#     assert "project_id" in data
#     assert data["created_by_id"] == user_data["id"]


def test_create_project(client, access_token_fixture):
    access_token = access_token_fixture
    fake_text = fake.text()
    fake_name = fake.company()
    user_data = create_user(client)
    response = client.post(
        "/projects/projects/", json={
            "project_name": fake_name,  # Generate a random company name as the project name
            "project_description":fake_text, # Generate a random text as the project description
            "created_by_id": fake.random_int(min=1, max=1000)  # Generate a random integer as the created_by_id
        }, headers={"Authorization": f"bearer {access_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["project_description"] == fake_text
    assert data["project_name"] == fake_name
    assert "updated_at" in data
    assert "created_at" in data
    assert "project_id" in data
    assert data["created_by_id"] == user_data["id"]
