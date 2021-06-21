import hashlib


def hashfy(content: str):
    return hashlib.md5(content.encode()).hexdigest()
