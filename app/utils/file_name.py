import uuid
import re


def format_filename(name, artist, album, file_ext):
    filename = f"{artist}-{album}-{name}.{file_ext}".replace(" ", "_")
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename) # Replace invalid characters with '_'
    return filename


def get_unique_filename(filename):
    ext = filename.rsplit(".", 1)[1].lower()
    unique_filename = uuid.uuid4().hex
    return f"{unique_filename}.{ext}"
