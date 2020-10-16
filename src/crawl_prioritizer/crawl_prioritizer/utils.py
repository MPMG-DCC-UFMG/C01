import hashlib
import tldextract

def hashfy(content: str):
    '''Turns content into an md5 hash in hexadecimal.
    '''
    return hashlib.md5(content.encode()).hexdigest()

def get_url_domain(url: str):
    '''Returns the domain of a URL.
    '''
    res = tldextract.extract(url)
    return f'{res.domain}.{res.suffix}'

