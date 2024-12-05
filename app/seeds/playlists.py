from app.models.db import db, environment, SCHEMA
from app.models import Playlist, Song, User
from sqlalchemy.sql import text

def seed_playlists():
    # Create playlists
    playlist1 = Playlist(
        user_id=1,
        name='Chill Vibes',
        description='Relaxing RPG tracks for focus and relaxation.'
    )
    playlist2 = Playlist(
        user_id=2,
        name='Epic Journeys',
        description='Music for epic adventures and explorations.'
    )
    playlist3 = Playlist(
        user_id=3,
        name='Boss Battle Themes',
        description='Intense tracks to pump up your adrenaline.'
    )
    playlist4 = Playlist(
        user_id=1,
        name='Boss Battle Themes',
        description='Intense tracks to pump up your adrenaline.'
    )
    playlist5 = Playlist(
        user_id=1,
        name='More Boss Battle Themes',
        description='Intense tracks to pump up your adrenaline.'
    )

    # Add songs to playlists
    song1 = Song.query.filter_by(name='Breezy').first()
    song2 = Song.query.filter_by(name='Compression of Time').first()
    song3 = Song.query.filter_by(name='Ending Theme').first()
    song4 = Song.query.filter_by(name='Eyes on Me').first()
    song5 = Song.query.filter_by(name='Junction').first()

    playlist1.songs.extend([song1, song2, song3, song4, song5])
    playlist2.songs.extend([song1, song2, song3, song4, song5])
    playlist3.songs.extend([song1, song2, song3, song4, song5])
    playlist4.songs.extend([song1, song2, song3, song4, song5])
    playlist5.songs.extend([song1, song2, song3, song4, song5])



    # Add playlists to the database
    db.session.add(playlist1)
    db.session.add(playlist2)
    db.session.add(playlist3)
    db.session.add(playlist4)
    db.session.add(playlist5)


    db.session.commit()

def undo_playlists():
    if environment == "production":
        db.session.execute(f"TRUNCATE table {SCHEMA}.playlists RESTART IDENTITY CASCADE;")
        db.session.execute(f"TRUNCATE table {SCHEMA}.playlist_songs RESTART IDENTITY CASCADE;")
    else:
        db.session.execute(text("DELETE FROM playlists"))
        db.session.execute(text("DELETE FROM playlist_songs"))
    db.session.commit()
