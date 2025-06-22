from core.auth import password_validation, create_access_token, get_username_from_token
from crud.crud_user import CRUDUser
from model.user import User
from util.common_function import is_valid_email

class AuthService:
    def __init__(self, db_session):
        self.db_session = db_session
        self.crud_user = CRUDUser(db_session)
    
    def register_user(self, username: str, email: str, password: str, full_name: str = None) -> User:
        
        if not password_validation(password):
            raise ValueError("Password does not meet strength requirements.")
        if not is_valid_email(email):
            raise ValueError("Invalid email format.")
        # Check if user already exists
        is_existing_user = self.crud_user.check_username_exist(username)
        if is_existing_user:
            raise ValueError("Username already exists.")
        is_existing_email = self.crud_user.check_email_exist(email)
        if is_existing_email:
            raise ValueError("Email already exists.")
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=password,  # In a real application, hash the password before storing
            full_name=full_name,
            portfolio_img_link=None
        )
        self.crud_user.create(new_user)
        return new_user
    
    def login_user(self, username: str, password: str) -> str:
        user = self.crud_user.get(User, {"username": username})
        if not user:
            user = self.crud_user.get(User, {"email": username})
        
        if not user or user.password != password:
            raise ValueError("Invalid username, email, or password.")
        
        # Create access token
        access_token = create_access_token({"username": user.username})
        return access_token
    
    def get_user_from_token(self, token: str):
        username = get_username_from_token(token)
        if not username:
            return None
        
        user = self.crud_user.get(User, {"username": username})
        return user
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        user = self.crud_user.get(User, {"username": username})
        if not user or user.password != old_password:
            raise ValueError("Invalid username or password.")
        
        if not password_validation(new_password):
            raise ValueError("New password does not meet strength requirements.")
        
        new_data = {
            "password": new_password  # In a real application, hash the password before storing
        }
        self.crud_user.update(user, new_data)
        return user
    
    def update_user(self, username: str, full_name: str = None, email: str = None) -> User:
        is_email_exist = self.crud_user.check_email_exist(email=email)
        if email and not is_valid_email(email):
            raise ValueError("Invalid email format.")
        if is_email_exist:
            raise ValueError("Email already exists.")
        user = self.crud_user.get(User, {"username": username})
        if not user:
            raise ValueError("User not found.")
        
        new_data = {}
        if full_name:
            new_data["full_name"] = full_name
        if email:
            new_data["email"] = email
        print(new_data)
        if new_data:
            self.crud_user.update(user, new_data)
        return user