from faker import Faker
from conftest import client
from routers.test_project import create_project
from routers.test_user import create_user


def create_task_status(client, task_status_name):
    response = client.post(
        "/tasks/task_statuses/", json={
            "task_status_name": task_status_name
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    return data


def test_create_task_status(client):
    task_status_name = fake.word()
    data = create_task_status(client, task_status_name)
    assert "task_status_id" in data
    assert data["task_status_name"] == task_status_name


fake = Faker()


def test_create_task(client, access_token_fixture):
    access_token = access_token_fixture
    # Generate fake user data
    user_data = create_user(client)
    project_data = create_project(client, access_token_fixture)
    task_status_name = fake.word()
    task_status_data = create_task_status(client, task_status_name)

    # Generate fake task data
    task_data = {
        "project_id": project_data['project_id'],
        "task_name": fake.sentence(),
        "task_description": fake.paragraph(),
        "task_owner_id": user_data['id'],
        "task_status_id": task_status_data['task_status_id']
    }
    response = client.post("/tasks/tasks/", json=task_data, headers={"Authorization": f"bearer {access_token}"})

    # Assert the response status code
    assert response.status_code == 200

    # Assuming you return the newly created task in the response
    created_task = response.json()

    # Assert the task details
    assert created_task["task_name"] == task_data["task_name"]
    assert created_task["task_description"] == task_data["task_description"]
