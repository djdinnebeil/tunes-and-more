import requests
from app.config import music_server_url


def handle_local_deletion(file_url):
    filename = file_url.split('/')[-1]
    local_server_url = f"{music_server_url}/{filename}"
    response = requests.delete(local_server_url)

    if response.status_code == 404:
        return 'Song record deleted successfully, but the song file was not found on the server.'
    elif response.status_code != 200:
        error_detail = response.json().get('error', 'Unknown error')
        return f'Failed to delete file from local server: {error_detail}, but record removed successfully'
    return 'Song deleted successfully from local server'
