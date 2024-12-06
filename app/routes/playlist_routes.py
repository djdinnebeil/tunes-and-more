from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Playlist, db, Song

playlist_routes = Blueprint('playlists', __name__)

@playlist_routes.route('/current', methods=['GET'])
@login_required
def get_user_playlists():
    user_id = current_user.id
    playlists = Playlist.query.filter_by(user_id=user_id).all()
    return jsonify([playlist.to_dict() for playlist in playlists])

@playlist_routes.route('/view', methods=['GET'])
@login_required
def view_user_playlists():
    user_id = current_user.id
    playlists = Playlist.query.filter_by(user_id=user_id).all()
    return render_template('playlists.html', playlists=[playlist.to_dict() for playlist in playlists])

@playlist_routes.route('/<int:playlist_id>', methods=['GET'])
@login_required
def get_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404
    return render_template('playlist_music_player.html', playlist=playlist.to_dict(), playlists=playlists)


@playlist_routes.route('/<int:playlist_id>/songs/<int:song_id>', methods=['POST', 'DELETE'])
@login_required
def remove_song_from_playlist(playlist_id, song_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    song = Song.query.get(song_id)
    if not song or song not in playlist.songs:
        return jsonify({"error": "Song not in playlist"}), 404

    playlist.songs.remove(song)
    db.session.commit()
    return jsonify({"message": "Song removed successfully", "song_id": song_id}), 200




@playlist_routes.route('/create', methods=['GET'])
@login_required
def create_playlist_form():
    songs = Song.query.all()
    return render_template('create_playlist.html', songs=[song.to_dict() for song in songs])


@playlist_routes.route('/create', methods=['POST'])
@login_required
def create_playlist():
    data = request.form
    name = data.get('name')
    song_ids = request.form.getlist('songs')  # List of selected song IDs

    if not name:
        return jsonify({"error": "Playlist name is required"}), 400

    new_playlist = Playlist(user_id=current_user.id, name=name)
    db.session.add(new_playlist)
    db.session.commit()

    # Add selected songs to the playlist
    for song_id in song_ids:
        song = Song.query.get(song_id)
        if song:
            new_playlist.songs.append(song)

    db.session.commit()
    return redirect(url_for('playlists.view_user_playlists'))


@playlist_routes.route('/<int:playlist_id>/edit', methods=['GET'])
@login_required
def edit_playlist_form(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    songs = Song.query.all()
    # Pass the IDs of current playlist songs
    playlist_song_ids = [song.id for song in playlist.songs]
    return render_template(
        'edit_playlist.html',
        playlist=playlist.to_dict(),
        songs=[song.to_dict() for song in songs],
        playlist_song_ids=playlist_song_ids
    )



@playlist_routes.route('/<int:playlist_id>/edit', methods=['POST'])
@login_required
def update_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    data = request.form
    name = data.get('name')
    song_ids = request.form.getlist('songs')  # List of selected song IDs

    if not name:
        return jsonify({"error": "Playlist name is required"}), 400

    playlist.name = name
    playlist.songs = []  # Clear existing songs

    # Add selected songs
    for song_id in song_ids:
        song = Song.query.get(song_id)
        if song:
            playlist.songs.append(song)

    db.session.commit()
    return redirect(url_for('playlists.view_user_playlists'))

@playlist_routes.route('/<int:playlist_id>/delete', methods=['POST'])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    db.session.delete(playlist)
    db.session.commit()
    return jsonify({"message": "Playlist deleted successfully"}), 200
