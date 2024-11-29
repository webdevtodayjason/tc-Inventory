from app import create_app, db
from app.models.user import User
import os

app = create_app()

@app.cli.command("create-admin")
def create_admin():
    """Create an admin user"""
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    
    user = User(username=username, email=email, role='admin')
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    print(f"Admin user {username} created successfully!")

# Add this to expose app to Flask CLI
def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port) 