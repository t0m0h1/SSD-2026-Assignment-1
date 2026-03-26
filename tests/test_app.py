import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

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




def test_register(client):

    response = client.post("/register", data={
        "username": "testuser",
        "password": "testpass123",
        "role": "patient"
    }, follow_redirects=True)

    assert response.status_code == 200

    # FIX: wrap DB query in app context
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        assert user is not None




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




if __name__ == "__main__":
    pytest.main()