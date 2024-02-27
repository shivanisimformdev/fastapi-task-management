# fastapi-task-management
Task Management Application

Clone the repository:
    `git clone git@github.com:shivanisimformdev/fastapi-task-management.git`

### Python Version
```
Python 3.10
```
### Installation

You can install the required packages using pip:

```bash
pip install -r requirements.txt
```
### Run FastAPI server

You can run fast API server from below command using uvicorn

```bash
uvicorn main:app --reload
```

## API Endpoints

### Create User

- **Description:** Creates a new user with the provided user details in the database.
- **Method:** POST
- **URL:** `/users/`
- **Request Body:** JSON object containing user details (username, email, password).
  ```json
  {
    "username": "example_user",
    "email": "user@example.com",
    "password": "password123"
  }

### Create User Role

- **Description:** Creates a new user role with the provided role details in the database.
- **Method:** POST
- **URL:** `/user_roles/`
- **Request Body:** JSON object containing role details.
  ```json
  {
    "role_name": "Administrator"
  }
  ```

## Create User Technology
- **Description:** Creates a new user technology with the provided technology details in the database.
- **Method:** POST
- **URL:** /user_technologies/
- **Request Body:** JSON object containing technology details.
```json
    {
    "technology_name": "Python"
    }
```