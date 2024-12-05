from .db import db, environment, SCHEMA, add_prefix_for_prod
from datetime import datetime

# Association table for playlists and songs
playlist_songs = db.Table(
    'playlist_songs',
    db.Model.metadata,
    db.Column('playlist_id', db.Integer, db.ForeignKey(add_prefix_for_prod('playlists.id')), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey(add_prefix_for_prod('songs.id')), primary_key=True),
    schema=SCHEMA if environment == "production" else None
)

class Playlist(db.Model):
    __tablename__ = 'playlists'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    user = db.relationship('User', back_populates='playlists')
    songs = db.relationship('Song', secondary=playlist_songs, back_populates='playlists')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'songs': [song.to_dict() for song in self.songs]
        }


