from flask import Blueprint, request, jsonify, current_app, render_template
from werkzeug.utils import secure_filename
import os
from app.models import db, Song, History
from flask_login import current_user, login_required
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON
from flask import send_from_directory
from datetime import datetime

song_routes = Blueprint('songs', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3'}

@song_routes.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_song_page():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            # Secure the file name
            filename = secure_filename(file.filename)

            # Save the file temporarily to extract metadata
            temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_path)

            relative_path = os.path.relpath(temp_path, current_app.root_path)

            print(relative_path, ' relative path line 34')

            # Extract metadata
            audio = MP3(temp_path, ID3=ID3)
            metadata = {
                'name': audio.get('TIT2').text[0] if 'TIT2' in audio else '',
                'artist': audio.get('TPE1').text[0] if 'TPE1' in audio else '',
                'album': audio.get('TALB').text[0] if 'TALB' in audio else '',
                'genre': audio.get('TCON').text[0] if 'TCON' in audio else '',
                'duration': int(audio.info.length) if audio.info else 0,
                'file_path': relative_path
            }

            # Render the form pre-populated with metadata
            return render_template('upload_song.html', metadata=metadata)

    # Default form render (empty fields)
    return render_template('upload_song.html', metadata={})

@song_routes.route('/upload/save', methods=['POST'])
def save_song():
    file_path = request.form.get('file_path')
    name = request.form.get('name', 'Unknown Title')
    artist = request.form.get('artist', 'Unknown Artist')
    album = request.form.get('album', None)
    genre = request.form.get('genre', None)
    duration = request.form.get('duration', 0)

    # Save song details in the database
    new_song = Song(
        user_id=current_user.id,
        name=name,
        artist=artist,
        album=album,
        genre=genre,
        duration=duration,
        file_url=file_path
    )
    db.session.add(new_song)
    db.session.commit()

    return jsonify(new_song.to_dict()), 201


@song_routes.route('/player', methods=['GET'])
@login_required
def music_player():
    # Fetch all songs uploaded by the current user
    songs = Song.query.all()

    return render_template('music_player.html', songs=songs)


@song_routes.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


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

