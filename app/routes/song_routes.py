from flask import Blueprint, request, jsonify, current_app, render_template
from werkzeug.utils import secure_filename
import os
from app.models import db, Song, History
from flask_login import current_user, login_required
from flask import send_from_directory
from datetime import datetime
import requests
from .aws_routes import upload_file_to_s3, get_unique_filename

song_routes = Blueprint('songs', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3'}

@song_routes.route('/upload', methods=['GET'])
@login_required
def upload_song_page():
    # Default form render (empty fields)
    return render_template('upload_song.html', metadata={})


@song_routes.route('/upload/save', methods=['POST'])
@login_required
def save_song():

    # Get metadata from the form
    name = request.form.get('name', 'Unknown Title')
    artist = request.form.get('artist', 'Unknown Artist')
    album = request.form.get('album', None)
    genre = request.form.get('genre', None)
    duration = request.form.get('duration', 0)
    file = request.files.get('file')
    file.filename = f"{artist}-{album}-{name}.mp3".replace(" ", "_")

    upload = upload_file_to_s3(file)

    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or missing file.'}), 400

    # Send file and metadata to the secondary server
    files = {'file': file}
    data = {
        'name': name,
        'artist': artist,
        'album': album
    }
    # response = requests.post('http://localhost:5000/upload', files=files, data=data)

    # if response.status_code != 200:
    #     return jsonify({'error': 'Failed to upload file to secondary server.'}), 500

    # Get file URL from the secondary server
    # file_url = response.json().get('file_url', '')
    # if not file_url:
    #     return jsonify({'error': 'Secondary server did not return file URL.'}), 500

    file_url = upload["url"]

    # Save song details in the database
    new_song = Song(
        user_id=current_user.id,
        name=name,
        artist=artist,
        album=album,
        genre=genre,
        duration=duration,
        file_url=file_url
    )
    db.session.add(new_song)
    db.session.commit()

    return jsonify(new_song.to_dict()), 201



@song_routes.route('/upload/local', methods=['GET'])
@login_required
def upload_song_page_local():
    # Default form render (empty fields)
    return render_template('upload_song_local.html', metadata={})


@song_routes.route('/upload/local/save', methods=['POST'])
@login_required
def save_song_local():
    # Get metadata from the form
    name = request.form.get('name', 'Unknown Title')
    artist = request.form.get('artist', 'Unknown Artist')
    album = request.form.get('album', None)
    genre = request.form.get('genre', None)
    duration = request.form.get('duration', 0)
    file = request.files.get('file')

    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or missing file.'}), 400

    # Send file and metadata to the secondary server
    files = {'file': file}
    data = {
        'name': name,
        'artist': artist,
        'album': album
    }
    response = requests.post('http://localhost:5000/upload', files=files, data=data)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to upload file to secondary server.'}), 500

    # Get file URL from the secondary server
    file_url = response.json().get('file_url', '')
    if not file_url:
        return jsonify({'error': 'Secondary server did not return file URL.'}), 500

    # Save song details in the database
    new_song = Song(
        user_id=current_user.id,
        name=name,
        artist=artist,
        album=album,
        genre=genre,
        duration=duration,
        file_url=file_url
    )
    db.session.add(new_song)
    db.session.commit()

    return jsonify(new_song.to_dict()), 201



@song_routes.route('/player', methods=['GET'])
@login_required
def music_player():
    # Fetch all songs uploaded by the current user
    songs = Song.query.all()
    serialized_songs = [song.to_dict() for song in songs]  # Serialize the Song objects
    return render_template('music_player.html', songs=serialized_songs)



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

from sqlalchemy.orm import joinedload

@song_routes.route('/history', methods=['GET'])
@login_required
def view_history():
    history = History.query.options(joinedload(History.song)).filter_by(user_id=current_user.id).order_by(History.last_played.desc()).all()
    history_data = [entry.to_dict() for entry in history]
    return render_template('listening_history.html', history=history_data)


from .aws_routes import remove_file_from_s3


@song_routes.route('/remove/<song_id>', methods=['GET'])
@login_required
def delete_song(song_id):
    song = Song.query.filter_by(id=song_id).first()
    if not song:
        return jsonify({"error": "Song not found"}), 404

    if song.user_id != current_user.id:
            return jsonify({"error": "Unauthorized"}), 403

    removed = remove_file_from_s3(song.file_url)

    if removed:
        # Delete the song record
        db.session.delete(song)
        db.session.commit()
        return jsonify({"message": "Song deleted successfully", "song_id": song_id, "name": song.name}), 200
    else:
        return jsonify({"error": "AWS bucket delete error"}), 400

