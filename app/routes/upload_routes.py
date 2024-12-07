from flask import Blueprint, request, jsonify, render_template
from flask_login import current_user, login_required
from app.models import db, Song, History, Playlist
from datetime import datetime
import requests
from .aws_routes import upload_file_to_s3, remove_file_from_s3
from sqlalchemy.orm import joinedload
from app.config import environment, music_server_url

upload_routes = Blueprint('upload', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3'}

@upload_routes.route('/', methods=['GET'])
@login_required
def upload_song_page():
    # Default form render (empty fields)
    songs = Song.query.filter_by(user_id=current_user.id).order_by(Song.created_at).all()
    if not songs:
        return render_template('upload_song.html', songs=[])
    songs = [entry.to_dict() for entry in songs]
    return render_template('upload_song.html', songs=songs)


@upload_routes.route('/save', methods=['POST'])
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

    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or missing file.'}), 400

    pre_url = f'{music_server_url}/{file.filename}'
    check_for_duplicate = Song.query.filter_by(file_url=pre_url).first()

    if check_for_duplicate is not None:
        return jsonify({'errors': 'A song with this file url already exists'}), 409

    if environment in ['production', 'aws-testing']:
        upload = upload_file_to_s3(file)
        if 'url' not in upload:
            upload['errors'].append("File upload failed.")
            return jsonify({'errors': upload['errors']}), 400
        file_url = upload['url']
    else:
        # Send file and metadata to the secondary server
        files = {'file': file}
        data = {'filename': file.filename}
        response = requests.post(music_server_url, files=files, data=data)

        if response.status_code != 200:
            return jsonify({'error': 'Failed to upload file to secondary server.'}), 500

        # Get file URL from the secondary server
        file_url = response.json().get('file_url', '')
        if not file_url:
            return jsonify({'error': 'Secondary server did not return file store.'}), 500

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

    # Create a history entry for the uploaded song with play_count=0
    new_history = History(
        user_id=current_user.id,
        song_id=new_song.id,
        play_count=0,
        last_played=None
    )
    db.session.add(new_history)
    db.session.commit()

    return jsonify(new_song.to_dict()), 201


@upload_routes.route('/current', methods=['GET'])
@login_required
def upload_history():
    upload_history = Song.query.filter_by(user_id=current_user.id).order_by(Song.created_at).all()
    if not upload_history:
        return []
    upload_history_data = [entry.to_dict() for entry in upload_history]
    return upload_history_data

@upload_routes.route('/update/<int:song_id>', methods=['PATCH'])
@login_required
def update_song(song_id):
    song = Song.query.get(song_id)

    if not song:
        return jsonify({"error": "Song not found"}), 404

    if song.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    # Get updated details from the request
    name = request.json.get('name', song.name)
    artist = request.json.get('artist', song.artist)
    album = request.json.get('album', song.album)
    genre = request.json.get('genre', song.genre)
    duration = request.json.get('duration', song.duration)

    # Update song details
    song.name = name
    song.artist = artist
    song.album = album
    song.genre = genre
    song.duration = duration

    db.session.commit()

    return jsonify(song.to_dict()), 200
