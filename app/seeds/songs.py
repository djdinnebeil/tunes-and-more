from app.models.db import db, environment, SCHEMA
from app.models import Song
from sqlalchemy.sql import text

# https://tunes-and-more-music.s3.us-east-1.amazonaws.com/
# https://tunes-and-more-music.s3.us-east-1.amazonaws.com/

def seed_songs():
    song1 = Song(
        user_id=1,
        name='Breezy',
        artist='FF8',
        album='OST',
        genre='RPG',
        duration=210,
        file_url='https://tunes-and-more-music.s3.us-east-1.amazonaws.com/FF8-OST-Breezy.mp3'
    )
    song2 = Song(
        user_id=1,
        name='Compression of Time',
        artist='FF8',
        album='OST',
        genre='RPG',
        duration=180,
        file_url='https://tunes-and-more-music.s3.us-east-1.amazonaws.com/FF8-OST-Compression_of_Time.mp3'
    )
    song3 = Song(
        user_id=2,
        name='Ending Theme',
        artist='FF8',
        album='OST',
        genre='RPG',
        duration=240,
        file_url='https://tunes-and-more-music.s3.us-east-1.amazonaws.com/FF8-OST-Ending_Theme.mp3'
    )
    song4 = Song(
        user_id=2,
        name='Eyes on Me',
        artist='FF8',
        album='OST',
        genre='RPG',
        duration=240,
        file_url='https://tunes-and-more-music.s3.us-east-1.amazonaws.com/FF8-OST-Eyes_on_Me.mp3'
    )
    song5 = Song(
        user_id=3,
        name='Junction',
        artist='FF8',
        album='OST',
        genre='RPG',
        duration=240,
        file_url='https://tunes-and-more-music.s3.us-east-1.amazonaws.com/FF8-OST-Junction.mp3'
    )

    song6 = Song(
        user_id=1,
        name='Blue Sky',
        artist='FF8',
        album='OST',
        genre='RPG',
        duration=240,
        file_url='https://tunes-and-more-music.s3.us-east-1.amazonaws.com/FF8-OST-Blue_Sky.mp3'
    )
    song7 = Song(
        user_id=1,
        name='Blue Fields',
        artist='FF8',
        album='OST',
        genre='RPG',
        duration=240,
        file_url='https://tunes-and-more-music.s3.us-east-1.amazonaws.com/FF8-OST-Blue_Fields.mp3'
    )
    song8 = Song(
        user_id=1,
        name='Under Her Control',
        artist='FF8',
        album='OST',
        genre='RPG',
        duration=240,
        file_url='https://tunes-and-more-music.s3.us-east-1.amazonaws.com/FF8-OST-Under_Her_Control.mp3'
    )
    song9 = Song(
        user_id=1,
        name='Data Screen',
        artist='FFT',
        album='OST',
        genre='RPG',
        duration=240,
        file_url='https://tunes-and-more-music.s3.us-east-1.amazonaws.com/FFT-OST-Data_Screen.mp3'
    )
    song10 = Song(
        user_id=1,
        name='Mission Complete',
        artist='FFT',
        album='OST',
        genre='RPG',
        duration=140,
        file_url='https://tunes-and-more-music.s3.us-east-1.amazonaws.com/FFT-OST-Mission_Complete.mp3'
    )
    song11 = Song(
        user_id=2,
        name='Windmill Hut',
        artist='Zelda',
        album='OST',
        genre='RPG',
        duration=140,
        file_url='https://tunes-and-more-music.s3.us-east-1.amazonaws.com/Zelda-OST-Windmill_Hut.mp3'
    )

    db.session.add(song1)
    db.session.add(song2)
    db.session.add(song3)
    db.session.add(song4)
    db.session.add(song5)
    db.session.add(song6)
    db.session.add(song7)
    db.session.add(song8)
    db.session.add(song9)
    db.session.add(song10)
    db.session.add(song11)

    db.session.commit()

def undo_songs():
    if environment == "production":
        db.session.execute(f"TRUNCATE table {SCHEMA}.songs RESTART IDENTITY CASCADE;")
    else:
        db.session.execute(text("DELETE FROM songs"))
    db.session.commit()
