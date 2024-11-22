from .db import db
from datetime import datetime

class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    play_count = db.Column(db.Integer, default=0)
    first_played = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_played = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='history')
    song = db.relationship('Song', back_populates='history')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'song_id': self.song_id,
            'play_count': self.play_count,
            'first_played': self.first_played.isoformat() if self.first_played else None,
            'last_played': self.last_played.isoformat() if self.last_played else None,
            'song': {
                'name': self.song.name,
                'artist': self.song.artist
            }
        }
