def get_connection():
    """Fake DB connection for CI."""
    return None

def insert_caption_entry(*args, **kwargs):
    return 123

def fetch_captions():
    return [{"Id": 1}]

def delete_caption_entry(caption_id):
    return True

def fetch_recent_captions():
    return [{"Id": 1}]
