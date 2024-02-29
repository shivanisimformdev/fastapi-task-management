from conftest import client


def create_user(client):
    response = client.post(
        "/users/", json={
            "username": "test02",
            "email": "test02@gmail.com",
            "password": "test"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    return data


def create_role(client, role_name):
    response = client.post(
        f"/users/user_roles/", json={
            "role_name": role_name
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    return data


def create_technology(client, technology_name):
    response = client.post(
        f"/users/user_technologies/", json={
            "technology_name": technology_name
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    return data


def create_user_details(client):
    response = client.post(
        "/users/user_details/", json={
            "user_id": 1,
            "user_role_id": 1,
            "user_technology_id": 1
        }
    )
    assert response.status_code == 200, response.text


def test_create_user(client):
    data = create_user(client)
    assert data["username"] == "test02"
    assert data["email"] == "test02@gmail.com"
    assert "password_hash" in data
    assert "id" in data


def test_create_role(client):
    role_name = "Engineer"
    data = create_role(client, role_name)
    assert data["role_name"] == role_name
    assert "user_role_id" in data


def test_create_technology(client):
    technology_name = "python"
    data = create_technology(client, technology_name)
    assert data["technology_name"] == "python"
    assert "user_technology_id" in data


def test_create_user_details(client):
    # user creation
    create_user(client)
    # user role creation
    role_name = "Engineer"
    create_role(client, role_name)
    # technology creation
    technology_name = "python"
    create_technology(client, technology_name)
    # user detail creation
    create_user_details(client)


def test_user_details(client):
    # user creation
    t = create_user(client)
    # user role creation
    role_name = "Engineer"
    create_role(client, role_name)
    # technology creation
    technology_name = "python"
    create_technology(client, technology_name)
    # user detail creation
    create_user_details(client)
    user_id = 1
    response = client.get(f"/users/{user_id}/details")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "created_at" in data
    assert "role_name" in data
    assert "technology_name" in data
    assert data["id"] == user_id
