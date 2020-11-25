import hashlib

def hashfy(content: str):
    '''Turns content into an md5 hash in hexadecimal.
    '''
    return hashlib.md5(content.encode()).hexdigest()
