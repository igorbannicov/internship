import sys

from app import create_app
from app.models.user import db, User

def create_user(username, password):
    """Creates a new user with a hashed password."""
    app = create_app()

    with app.app_context():
        db.create_all()  # Ensure tables exist

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            print(f"User '{username}' already exists!")
            return
        
        # Create a new user
        user = User(username=username)
        user.set_password(password)  # Hash the password
        db.session.add(user)
        db.session.commit()
        
        print(f"User '{username}' created successfully!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python utils/create_user.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    create_user(username, password)
