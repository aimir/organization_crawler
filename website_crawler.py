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
FORBIDDEN_URL_SUBSTRINGS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.woff', '.woff2',
                            '.css', '.ttf', '.mp3', '.mp4', '.wav', '.map', '.ico', '.pdf']
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
ALLOWED_SCHEMES = ['http', 'https']
FORBIDDEN_DOMAINS = ['unpkg.com', 'fonts.googleapis.com', 'www.youtube.com', 'www.w3.org',
                     'www.linkedin.com', 'www.facebook.com', 'www.google.com',
                     'polymer.github.io', 'open.spotify.com', 'underscorejs.org',
                     'openjsf.org', 'npms.io', 'fb.me', 'mailchi.mp', 'api.whatsapp.com',
                     'sentry.io', 'secure.gravatar.com', 'github.com', 'lodash.com',
                     'discord.gg', 'kit.fontawesome.com', 'il.linkedin.com', 'api.jqueryui.com',
                     'getbootstrap.com', 'getbootstrap.com', 'microsoft.com']
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
    likely_urls = set([match[0].decode('utf-8') for match in (re.findall(URL_REGEX1, resp.content) +
                                              re.findall(URL_REGEX2, resp.content))
                                              if all(word not in match[0].decode('utf-8')
                                                     for word in FORBIDDEN_URL_SUBSTRINGS)])
    found_urls = set()
    for likely_url in likely_urls:
        try:
            absolute_url = urllib.parse.urljoin(base_url, likely_url)
            defraged_url = urllib.parse.urldefrag(absolute_url).url
            parts = urllib.parse.urlparse(defraged_url)
        except ValueError:
            print
            pass
        else:
            if (parts.scheme.lower() in ALLOWED_SCHEMES
                and parts.netloc.lower() not in FORBIDDEN_DOMAINS):
                found_urls.add(defraged_url)
    return found_urls

def get_records_by_website(website_names):
    result = {}

    for domain in website_names:
        print("Scraping ", domain)
        base_url = domain
        if not base_url.startswith('http'):
            base_url = 'https://' + base_url
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
                print(scraped_count, '/', len(to_query_queue)+scraped_count, " [found " + str(len(seen_urls)) + "]")
        result[domain] = list(seen_urls)
    return result

