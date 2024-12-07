from app.models.db import db, environment, SCHEMA
from app.models import Playlist, Song, User
from sqlalchemy.sql import text

def seed_playlists():
    # Bulk insert playlists
    playlists = [
        Playlist(user_id=1, name='Chill Vibes'),
        Playlist(user_id=2, name='Epic Journeys'),
        Playlist(user_id=3, name='Boss Battle Themes'),
        Playlist(user_id=1, name='Bowser Battle Themes'),
        Playlist(user_id=1, name='The Orange King'),
    ]

    db.session.bulk_save_objects(playlists)
    db.session.commit()

    # Retrieve songs from the database
    song1 = Song.query.filter_by(name='Breezy').first()
    song2 = Song.query.filter_by(name='Compression of Time').first()
    song3 = Song.query.filter_by(name='Ending Theme').first()
    song4 = Song.query.filter_by(name='Eyes on Me').first()
    song5 = Song.query.filter_by(name='Junction').first()
    song6 = Song.query.filter_by(name='Mission Complete').first()
    song7 = Song.query.filter_by(name='Windmill Hut').first()

    # Update playlist-song relationships
    playlists[0].songs.extend([song1, song2, song3, song4, song5])  # Chill Vibes
    playlists[1].songs.extend([song6, song2, song3, song4])         # Epic Journeys
    playlists[2].songs.extend([song7, song2, song3, song4, song5])  # Boss Battle Themes
    playlists[3].songs.extend([song6, song3, song4, song5])         # Bowser Battle Themes
    playlists[4].songs.extend([song7, song4, song5])                # The Orange King

    # Save the relationships
    db.session.add_all(playlists)
    db.session.commit()

def undo_playlists():
    if environment == "production":
        db.session.execute(f"TRUNCATE table {SCHEMA}.playlists RESTART IDENTITY CASCADE;")
        db.session.execute(f"TRUNCATE table {SCHEMA}.playlist_songs RESTART IDENTITY CASCADE;")
    else:
        db.session.execute(text("DELETE FROM playlists"))
        db.session.execute(text("DELETE FROM playlist_songs"))
    db.session.commit()
