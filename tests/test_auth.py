from bs4 import BeautifulSoup
import pytest
from app import create_app, db
from app.models.user import User
from app.models.config import Configuration
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_register(client):
    Configuration.set_value('allow_public_registration', 'true')
    form = client.get('/register')
    assert form.status_code == 200
    token = BeautifulSoup(form.data, 'html.parser').find('input', {'name': 'csrf_token'})['value']
    response = client.post('/register', data={
        'csrf_token': token,
        'pin': '123456',
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful!' in response.data
    
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'test@example.com'

def test_login_logout(client):
    # Create test user
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    # Test login
    form = client.get('/login')
    assert form.status_code == 200
    token = BeautifulSoup(form.data, 'html.parser').find('input', {'name': 'csrf_token'})['value']
    response = client.post('/login', data={
        'csrf_token': token,
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert session['_user_id'] == str(user.id)
    assert b'Dashboard' in response.data
    
    # Test logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert '_user_id' not in session
    assert b'Login' in response.data
