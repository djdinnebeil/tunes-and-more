from flask import Blueprint, request, jsonify, render_template
from flask_login import current_user, login_required
from app.models import db, Song, History, Playlist
from datetime import datetime
import requests
from .aws_routes import upload_file_to_s3, remove_file_from_s3
from sqlalchemy.orm import joinedload
from app.config import environment, music_server_url

song_routes = Blueprint('songs', __name__)

@song_routes.route('/', methods=['GET'])
@login_required
def music_player():
    # Fetch all songs uploaded by the current user
    songs = Song.query.filter_by(user_id=current_user.id).all()
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    serialized_songs = [song.to_dict() for song in songs]  # Serialize the Song objects
    return render_template('music_player.html', songs=serialized_songs, playlists=playlists)


@song_routes.route('/current', methods=['GET'])
@login_required
def get_songs():
    songs = Song.query.filter_by(user_id=current_user.id).all()  # Filter songs by user
    return jsonify([song.to_dict() for song in songs])


@song_routes.route('/play/<int:song_id>', methods=['POST'])
def update_play_count(song_id):
    history = History.query.filter_by(user_id=current_user.id, song_id=song_id).first()
    if not history:
        # Create a new history entry if it doesn't exist
        history = History(user_id=current_user.id, song_id=song_id, play_count=1)
    else:
        # Update play count and last played time
        history.play_count += 1

    history.last_played = datetime.now()

    db.session.add(history)
    db.session.commit()

    return jsonify(history.to_dict()), 200

