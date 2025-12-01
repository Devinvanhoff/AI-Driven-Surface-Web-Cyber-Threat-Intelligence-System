import requests
from bs4 import BeautifulSoup

def scrape_text(url, timeout=10):
    '''
    Simple scraper: fetches URL and returns concatenated text from <article>, <p>, and <div> tags.
    NOTE: This prototype does NOT perform robots.txt checks. For production, ALWAYS respect robots.txt and terms of service.
    '''
    headers = {'User-Agent': 'KU-Topup-Prototype/1.0 (+https://example.com)'}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        return f"ERROR: {str(e)}"

    soup = BeautifulSoup(resp.text, 'html.parser')
    texts = []
    for tag in soup.find_all(['article','p','div']):
        t = tag.get_text(separator=' ', strip=True)
        if len(t) > 60:
            texts.append(t)
    if not texts:
        # fallback: full page text
        full = soup.get_text(separator=' ', strip=True)
        if len(full) < 10:
            return 'ERROR: No readable text found on page'
        return full[:5000]
    # return a reasonable chunk
    return '\n\n'.join(texts)[:5000]


