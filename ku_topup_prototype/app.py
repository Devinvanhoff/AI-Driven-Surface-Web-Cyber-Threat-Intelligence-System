from flask import Flask, request, jsonify, render_template, redirect, url_for
from scraper import scrape_text
from classifier import classify_text

app = Flask(__name__)

# 🏠 Landing page
@app.route('/')
def index():
    return render_template('index.html')

# 🔍 Scanning dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# 🧠 Handle scanning + redirect to report
@app.route('/scrape-and-classify', methods=['POST'])
def scrape_and_classify_route():
    user_input = request.form.get('url', '').strip()

    # If the input looks like a URL, scrape it — else treat it as text
    if user_input.startswith('http://') or user_input.startswith('https://'):
        scraped = scrape_text(user_input)
        if scraped.startswith('ERROR:'):
            return jsonify({'error': scraped}), 400
        text_to_classify = scraped
    else:
        # Treat as plain text
        text_to_classify = user_input

    # Classify content
    label, score, indicators = classify_text(text_to_classify, use_ai=True)

    # Redirect with results
    return redirect(url_for(
        'report',
        url=user_input,
        label=label,
        score=score,
        indicators=",".join(indicators)
    ))

# 📊 Report page
@app.route('/report')
def report():
    url = request.args.get('url')
    label = request.args.get('label')
    score = request.args.get('score')
    indicators = request.args.get('indicators', '').split(',')
    return render_template('report.html', url=url, label=label, score=score, indicators=indicators)

if __name__ == '__main__':
    app.run(debug=True)













