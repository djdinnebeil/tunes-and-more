from app.models.db import db, environment, SCHEMA
from app.models import Song
from sqlalchemy.sql import text

def seed_songs():
    song1 = Song(
        user_id=1,
        name='Breezy',
        artist='FF8',
        album='OST',
        genre='RPG',
        duration=210,
        file_url='http://localhost:5000/files/FF8-OST-Breezy.mp3'
    )
    song2 = Song(
        user_id=1,
        name='Compression of Time',
        artist='FF8',
        album='OST',
        genre='RPG',
        duration=180,
        file_url='http://localhost:5000/files/FF8-OST-Compression_of_Time.mp3'
    )
    song3 = Song(
        user_id=2,
        name='Ending Theme',
        artist='FF8',
        album='OST',
        genre='RPG',
        duration=240,
        file_url='http://localhost:5000/files/FF8-OST-Ending_Theme.mp3'
    )
    song4 = Song(
        user_id=2,
        name='Eyes on Me',
        artist='FF8',
        album='OST',
        genre='RPG',
        duration=240,
        file_url='http://localhost:5000/files/FF8-OST-Eyes_on_Me.mp3'
    )
    song5 = Song(
        user_id=3,
        name='Junction',
        artist='FF8',
        album='OST',
        genre='RPG',
        duration=240,
        file_url='http://localhost:5000/files/FF8-OST-Junction.mp3'
    )
    db.session.add(song1)
    db.session.add(song2)
    db.session.add(song3)
    db.session.add(song4)
    db.session.add(song5)

    db.session.commit()

def undo_songs():
    if environment == "production":
        db.session.execute(f"TRUNCATE table {SCHEMA}.songs RESTART IDENTITY CASCADE;")
    else:
        db.session.execute(text("DELETE FROM songs"))
    db.session.commit()
