import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import User
from werkzeug.security import generate_password_hash
from app import is_valid_username
from app import is_strong_password


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


# test for valid username
def test_invalid_username_short():
    valid, msg = is_valid_username("ab")
    assert not valid

def test_invalid_username_chars():
    valid, msg = is_valid_username("bad@name")
    assert not valid

def test_valid_username():
    valid, msg = is_valid_username("valid_user123")
    assert valid




def test_password_too_short():
    valid, _ = is_strong_password("Ab1!")
    assert not valid

def test_password_missing_uppercase():
    valid, _ = is_strong_password("password123!")
    assert not valid

def test_password_valid():
    valid, _ = is_strong_password("StrongPass1!")
    assert valid


# test for user registration
def test_register_success(client):
    response = client.post("/register", data={
        "username": "newuser",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects=True)

    assert b"Account created" in response.data


# test for login with valid credentials
def test_login(client):

    with app.app_context():
        user = User(
            username="loginuser",
            password_hash=generate_password_hash("testpass123"),
            role="patient"
        )
        db.session.add(user)
        db.session.commit()

    response = client.post("/login", data={
        "username": "loginuser",
        "password": "testpass123"
    }, follow_redirects=True)

    assert response.status_code == 200






# no tests below this line

if __name__ == "__main__":
    pytest.main()