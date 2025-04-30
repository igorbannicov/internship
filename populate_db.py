from app import create_app, db
from app.models import User

app = create_app()
app.app_context().push()

def init_db():
    print("Creating all tables...")
    db.create_all()

def create_admin():
    email = "admin@example.com"
    password = "p4ssw0rd"
    name = "Admin User"

    if User.query.filter_by(email=email).first():
        print("Admin already exists.")
        return

    admin = User(email=email, name=name, role="admin")
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print("Admin user created.")

if __name__ == "__main__":
    init_db()
    create_admin()
