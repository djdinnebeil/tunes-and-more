from app.models.db import db, environment, SCHEMA
from app.models import Playlist, Song
from sqlalchemy.sql import text

def seed_playlists():
    playlist1 = Playlist(
        user_id=1,
        name='Chill Vibes',
    )
    playlist2 = Playlist(
        user_id=2,
        name='Epic Journeys'
    )
    playlist3 = Playlist(
        user_id=3,
        name='Boss Battle Themes',
    )
    playlist4 = Playlist(
        user_id=1,
        name='Bowser Battle Themes',
    )
    playlist5 = Playlist(
        user_id=1,
        name='The Orange King',
    )

    song1 = Song.query.filter_by(name='Breezy').first()
    song2 = Song.query.filter_by(name='Compression of Time').first()
    song3 = Song.query.filter_by(name='Ending Theme').first()
    song4 = Song.query.filter_by(name='Eyes on Me').first()
    song5 = Song.query.filter_by(name='Junction').first()
    song6 = Song.query.filter_by(name='Mission Complete').first()
    song7 = Song.query.filter_by(name='Windmill Hut').first()

    playlist1.songs.extend([song1, song2, song3, song4, song5])
    playlist2.songs.extend([song6, song2, song3, song4])
    playlist3.songs.extend([song7, song2, song3, song4, song5])
    playlist4.songs.extend([song6, song3, song4, song5])
    playlist5.songs.extend([song7, song4, song5])

    # Add playlists to the database
    db.session.add(playlist1)
    db.session.add(playlist2)
    db.session.add(playlist3)
    db.session.add(playlist4)

    db.session.commit()

def undo_playlists():
    if environment == "production":
        db.session.execute(f"TRUNCATE table {SCHEMA}.playlists RESTART IDENTITY CASCADE;")
        db.session.execute(f"TRUNCATE table {SCHEMA}.playlist_songs RESTART IDENTITY CASCADE;")
    else:
        db.session.execute(text("DELETE FROM playlists"))
        db.session.execute(text("DELETE FROM playlist_songs"))
    db.session.commit()
