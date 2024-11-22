from app.models.db import db, environment, SCHEMA
from app.models import History
from sqlalchemy.sql import text
from datetime import datetime

def seed_history():
    history1 = History(
        user_id=1,
        song_id=1,
        play_count=10,
        first_played=datetime(2024, 1, 1),
        last_played=datetime(2024, 11, 20)
    )
    history2 = History(
        user_id=1,
        song_id=2,
        play_count=5,
        first_played=datetime(2024, 1, 10),
        last_played=datetime(2024, 11, 21)
    )
    history3 = History(
        user_id=2,
        song_id=3,
        play_count=8,
        first_played=datetime(2024, 2, 15),
        last_played=datetime(2024, 11, 22)
    )

    db.session.add(history1)
    db.session.add(history2)
    db.session.add(history3)
    db.session.commit()

def undo_history():
    if environment == "production":
        db.session.execute(f"TRUNCATE table {SCHEMA}.history RESTART IDENTITY CASCADE;")
    else:
        db.session.execute(text("DELETE FROM history"))
    db.session.commit()
