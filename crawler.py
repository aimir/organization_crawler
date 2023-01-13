import requests
from bs4 import BeautifulSoup
import re
import urllib
import time
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

REAL_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
           'Chrome/106.0.0.0 Safari/537.36')
# TODO: unify those two to avoid duplicates
URL_REGEX1 = b'href *?= *?[\'"](.*?)([\'"])'
URL_REGEX2 = (b'(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}'
              b'(/[-a-zA-Z0-9()@:%_\+.~#?&//=]*)?)')
FORBIDDEN_URL_SUBSTRINGS = [b'.jpg', b'.jpeg', b'.png', b'.gif', b'.bmp', b'.woff', b'.woff2',
                            b'.css', b'.ttf', b'.mp3', b'.mp4', b'.wav', b'.map', b'.ico', b'.pdf']
ALLOWED_CONTENT = ['text/plain', 'application/json', 'text/html', 'application/javascript',
                   'text/javascript', 'text/csv', 'application/xhtml+xml', 'application/xml',
                   'text/xml', 'application/rss+xml', 'application/x-javascript']
FORBIDDEN_CONTENT = ['application/octet-stream', 'font/woff2', 'font/woff', 'image/webp',
                     'text/css', 'image/vnd.microsoft.icon', 'image/gif', 'application/pdf',
                     'image/svg+xml', 'audio/aac', 'image/bmp', 'application/x-bzip',
                     'application/x-bzip2', 'application/gzip', 'image/jpeg', 'audio/midi',
                     'audio/x-midi', 'audio/mpeg', 'video/mp4', 'video/mpeg', 'image/png',
                     'application/x-tar', 'image/tiff', 'font/ttf', 'audio/wav', 'audio/webm',
                     'video/webm', 'image/webp', 'application/zip', 'application/x-7z-compressed',
                     'image/x-icon', 'application/manifest+json', 'binary/octet-stream',
                     'application/x-javascript', 'application/vnd.ms-fontobject',
                     'application/rdf+xml']
# How long to wait before the first request, between the first and second, etc.
BACKOFF_REQUEST_TIMES = [0, 0, 0]
ALLOWED_SCHEMES = [b'http', b'https']
FORBIDDEN_DOMAINS = [b'unpkg.com', b'fonts.googleapis.com', b'www.youtube.com', b'www.w3.org',
                     b'www.linkedin.com', b'www.facebook.com', b'www.google.com',
                     b'polymer.github.io', b'open.spotify.com', b'underscorejs.org',
                     b'openjsf.org', b'npms.io', b'fb.me', b'mailchi.mp', b'api.whatsapp.com',
                     b'sentry.io', b'secure.gravatar.com', b'github.com', b'lodash.com',
                     b'discord.gg', b'kit.fontawesome.com', b'il.linkedin.com', b'api.jqueryui.com',
                     b'getbootstrap.com', 'getbootstrap.com']
MAX_DEPTH = 3
CONNECTION_TIMEOUT = 10 # seconds

def extract_links(base_url):
    # TODO: actually robo-browse via selenium to bypass anti-scraping machinery
    resp_ok = False
    backoff_array_index = 0
    while not resp_ok:
        if backoff_array_index >= len(BACKOFF_REQUEST_TIMES):
            # Give up :(
            return []
        # Otherwise, sleep and retry
        time.sleep(BACKOFF_REQUEST_TIMES[backoff_array_index])
        backoff_array_index += 1
        try:
            resp = requests.get(base_url, headers={'User-Agent': REAL_UA}, verify=False,
                                timeout=CONNECTION_TIMEOUT)
            resp_ok = resp.ok
        except requests.exceptions.RequestException:
            pass

    # Validate content type:
    content_type = resp.headers.get('Content-Type', 'text/plain').split(';')[0].split(', ')[0]
    assert (content_type in ALLOWED_CONTENT
            or content_type in FORBIDDEN_CONTENT), ('Unfamiliar Content-Type: ' + content_type +
                                                    ' at ' + base_url.decode())
    if content_type in FORBIDDEN_CONTENT:
        return []

    # Filter relevant urls:
    likely_urls = set([match[0] for match in (re.findall(URL_REGEX1, resp.content) +
                                              re.findall(URL_REGEX2, resp.content))
                                              if all(word not in match[0]
                                                     for word in FORBIDDEN_URL_SUBSTRINGS)])
    found_urls = set()
    for likely_url in likely_urls:
        try:
            absolute_url = urllib.parse.urljoin(base_url, likely_url)
            parts = urllib.parse.urlparse(absolute_url)
        except ValueError:
            pass
        else:
            if (parts.scheme.lower() in ALLOWED_SCHEMES
                and parts.netloc.lower() not in FORBIDDEN_DOMAINS):
                found_urls.add(absolute_url)
    return found_urls

result = {}

for domain in [b'firstime.vc']:
    base_url = b'https://' + domain + '/'
    seen_urls = {base_url}
    to_query_queue = [(base_url, 0)]
    scraped_count = 0

    while to_query_queue:
        # TODO: async requests
        url, depth = to_query_queue[0]
        to_query_queue = to_query_queue[1:]
        for new_url in extract_links(url):
            # TODO: properly canonicalize URLs
            if not new_url in seen_urls and depth < MAX_DEPTH:
                seen_urls.add(new_url)
                if domain in new_url:
                    to_query_queue.append((new_url, depth + 1))
        scraped_count += 1
        if scraped_count % 10 == 0:
            print(scraped_count, '/', len(seen_urls))
    result[domain] = list(seen_urls)
