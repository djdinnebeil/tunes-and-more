from app.models.db import db, environment, SCHEMA
from app.models import User
from werkzeug.security import generate_password_hash
from sqlalchemy.sql import text

def seed_users():
    user1 = User(username='demo@aa.io', email='demo@aa.io', password='password')
    user2 = User(username='djdinnebeil@aa.io', email='djdinnebeil@aa.io', password='password')
    user3 = User(username='dd42@aa.io', email='dd42@aa.io', password='password')

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)

    db.session.commit()


def undo_users():
    if environment == "production":
        db.session.execute(f"TRUNCATE table {SCHEMA}.users RESTART IDENTITY CASCADE;")
    else:
        db.session.execute(text("DELETE FROM users"))

    db.session.commit()
