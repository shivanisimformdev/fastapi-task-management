from utils.hash_pwd import hash_password
from faker import Faker
from models.user import User
from models.project import Project, UserProject
from database.session import SessionLocal

faker = Faker()

db = SessionLocal()

if __name__ == "__main__":
    for i in range(0, 50):
        password = "password"
        user = User(username=faker.user_name(),
                    email=faker.email(),
                    password_hash=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)
        project = Project(project_name=faker.name(),
                project_description=faker.paragraph(),
                created_by_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)
        user_projects = UserProject(user_id=user.id,
                project_id=project.project_id,
                )
        db.add(user_projects)
        db.commit()
        db.refresh(user_projects)

# kristin78@example.net
# ericweaver@example.net
# keith82@example.net
# johnsonjoe@example.com
# jameslindsey@example.org
