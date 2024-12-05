from flask import Blueprint, request, jsonify, current_app, render_template
from werkzeug.utils import secure_filename
import os
from app.models import db, Song, History, Playlist
from flask_login import current_user, login_required
from flask import send_from_directory
from datetime import datetime
import requests
from .aws_routes import upload_file_to_s3, get_unique_filename, remove_file_from_s3
from sqlalchemy.orm import joinedload

environment = os.getenv("FLASK_ENV")

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



    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or missing file.'}), 400

    if environment in ['production', 'aws-testing']:
        pre_url = f'https://tunes-and-more-music.s3.us-east-1.amazonaws.com/{file.filename}'
        check_for_duplicate = Song.query.filter_by(file_url=pre_url).first()

        if check_for_duplicate is not None:
            return jsonify({'errors': 'A song with this file url already exists'}), 409

        upload = upload_file_to_s3(file)
        if 'url' not in upload:
            upload['errors'].append("File upload failed.")
            return jsonify({'errors': upload['errors']}), 400
        file_url = upload["url"]
    else:
        # Send file and metadata to the secondary server
        files = {'file': file}
        data = {
            'name': name,
            'artist': artist,
            'album': album,
            'filename': file.filename
        }
        pre_url = f'http://localhost:5000/files/{file.filename}'
        check_for_duplicate = Song.query.filter_by(file_url=pre_url).first()

        if check_for_duplicate is not None:
            return jsonify({'errors': 'A song with this file url already exists'}), 409

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



@song_routes.route('/player', methods=['GET'])
@login_required
def music_player():
    # Fetch all songs uploaded by the current user
    songs = Song.query.filter_by(user_id=current_user.id).all()
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    serialized_songs = [song.to_dict() for song in songs]  # Serialize the Song objects
    return render_template('music_player.html', songs=serialized_songs, playlists=playlists)


@song_routes.route('/', methods=['GET'])
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



@song_routes.route('/remove/<song_id>', methods=['GET'])
@login_required
def delete_song(song_id):
    # song = Song.query.filter_by(id=song_id).first()
    song = Song.query.get(song_id)

    if not song:
        return jsonify({"error": "Song not found"}), 404

    if song.user_id != current_user.id:
            return jsonify({"error": "Unauthorized"}), 403

    if environment in ['production', 'aws-testing']:
        removed = remove_file_from_s3(song.file_url)
        if not removed:
            return jsonify({"error": "AWS bucket delete error"}), 400
    else:
        # Local deletion logic
        file_url = song.file_url
        filename = file_url.split('/')[-1]  # Extract the filename from the URL
        local_server_url = f"http://localhost:5000/files/{filename}"
        print('local server url', local_server_url)


        response = requests.delete(local_server_url)
        if response.status_code != 200:
            return jsonify({"error": f"Failed to delete file from local server: {response.json().get('error', 'Unknown error')}"}), 500

    # Delete the song record
    db.session.delete(song)
    db.session.commit()
    return jsonify({"message": "Song deleted successfully", "song_id": song_id, "name": song.name}), 200



@song_routes.route('/history', methods=['GET'])
@login_required
def view_history():
    history = History.query.options(joinedload(History.song)).filter_by(user_id=current_user.id).order_by(History.play_count.desc()).all()
    history_data = [entry.to_dict() for entry in history]
    return render_template('listening_history.html', history=history_data)



@song_routes.route('/history/reset/<int:history_id>', methods=['POST'])
@login_required
def reset_play_count(history_id):
    history_entry = History.query.filter_by(user_id=current_user.id, id=history_id).first()
    if not history_entry:
        return jsonify({"error": "History entry not found"}), 404

    history_entry.play_count = 0
    history_entry.last_played = None

    db.session.commit()
    return jsonify({"message": "Play count reset successfully", "history_id": history_id}), 200


@song_routes.route('/history/remove/<int:history_id>', methods=['DELETE'])
@login_required
def remove_from_history(history_id):
    history_entry = History.query.filter_by(user_id=current_user.id, id=history_id).first()
    if not history_entry:
        return jsonify({"error": "History entry not found"}), 404

    db.session.delete(history_entry)
    db.session.commit()
    return jsonify({"message": "Song removed from history", "song_id": history_id}), 200


@song_routes.route('/upload/history', methods=['GET'])
@login_required
def upload_history():
    upload_history = Song.query.filter_by(user_id=current_user.id).order_by(Song.created_at).all()
    if not upload_history:
        return []
    upload_history_data = [entry.to_dict() for entry in upload_history]
    return upload_history_data


@song_routes.route('/update/<int:song_id>', methods=['PATCH'])
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
