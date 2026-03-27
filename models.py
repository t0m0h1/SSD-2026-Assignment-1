from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    # users.db 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")


class PatientRecord(db.Model):
    # Stored in records.db
    __bind_key__ = "records"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.String(50), unique=True, nullable=False)

    age = db.Column(db.Integer)
    sex = db.Column(db.String(10))

    blood_pressure = db.Column(db.Integer)
    cholesterol = db.Column(db.Integer)

    fasting_blood_sugar = db.Column(db.String(10))
    resting_ecg = db.Column(db.String(20))
    angina = db.Column(db.String(10))

    last_updated = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    # Stored in records.db
    __bind_key__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50))  # could upgrade to user_id later
    action = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


def log_action(user, action):
    try:
        log = AuditLog(user=user, action=action)
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()




class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("User", backref="appointments")