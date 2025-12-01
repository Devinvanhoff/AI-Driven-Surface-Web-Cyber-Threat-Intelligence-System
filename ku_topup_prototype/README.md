# KU Topup — Prototype (25% deliverable)

This prototype includes:
- A simple Flask backend (`app.py`) with endpoints to classify text and to scrape+classify a URL.
- `scraper.py`: a small scraping helper using `requests` + `bs4` (BeautifulSoup).
- `classifier.py`: a lightweight keyword-based classifier (prototype; swap in ML later).
- `sample_data.csv`: a few example forum posts (for testing / interim report).
- `requirements.txt`: suggested packages.

## How to run (locally)
1. Create a Python venv and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   If `bs4` or `flask` are missing, install them manually:
   ```bash
   pip install flask requests beautifulsoup4
   ```
3. Run the server:
   ```bash
   python app.py
   ```
4. Test endpoints (examples using `curl`):
   - Classify raw text:
     ```bash
     curl -X POST http://127.0.0.1:5000/classify-text -H "Content-Type: application/json" -d '{"text":"This forum post mentions leaked passwords and a database dump."}'
     ```
   - Scrape a URL and classify:
     ```bash
     curl -X POST http://127.0.0.1:5000/scrape-and-classify -H "Content-Type: application/json" -d '{"url":"https://example.com/article"}'
     ```

## Notes
- This is a prototype to satisfy your interim deliverable (roughly 25% of the final system): basic ingestion (scraper), basic analysis (classifier), and an API to connect to a later React dashboard.
- Next steps (recommended): integrate a supervised ML model, store results in a DB, add external API checks (VirusTotal / Have I Been Pwned), expand scrapers with Scrapy, and build a frontend dashboard in React.
