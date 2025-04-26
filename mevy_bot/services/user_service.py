from sqlalchemy.orm import Session
from mevy_bot.models.user import User

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, email: str, name: str, password_hash: bytes) -> None:
        new_user = User(
            email=email,
            name=name,
            password_hash=password_hash
        )
        self.db.add(new_user)
        self.db.commit()
