import os
import re
import requests
from hibp_api import check_email_pwned

# ---------- CONFIG ----------
HF_API_URLS = [
    "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"
]

HF_TOKEN = "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"
# -----------------------------

# Expanded threat keywords
KEYWORDS = [
    'exploit', 'leak', 'leaked', 'password', 'credentials', 'dump',
    'breach', 'ransomware', 'malware', 'virus', 'trojan', 'worm',
    'cve', 'botnet', 'pwned', 'vulnerability', 'zero-day', 'zero day',
    'sql injection', 'sqli', 'xss', 'remote code execution', 'rce',
    'payload', 'phishing', 'spyware', 'backdoor', 'stealer',
    'compromise', 'attack', 'infection', 'command and control', 'c2'
]

EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
IP_RE = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
HASH_RE = re.compile(r'\b[a-f0-9]{32,128}\b', re.I)


def classify_text(text, use_ai=True):
    if not text:
        return 'non-threat', 0, []

    indicators = []
    score = 0.0
    t = text.lower()

    # 1️⃣ Keyword-based scoring
    for kw in KEYWORDS:
        if kw in t:
            indicators.append(kw)
            score += 1.0

    # 2️⃣ Email checks with HIBP
    emails = EMAIL_RE.findall(text)
    if emails:
        for e in emails:
            try:
                p = check_email_pwned(e)
            except Exception:
                p = None
            if p is True:
                indicators.append(f"{e} → found in breaches")
                score += 2.0
            elif p is False:
                indicators.append(f"{e} → not found in breaches")
                score += 1.0
            else:
                indicators.append(f"{e} → HIBP check unavailable")
                score += 0.5

    # 3️⃣ IP and hash detection
    if IP_RE.search(text):
        indicators.append('ip_address')
        score += 1.0
    if HASH_RE.search(text):
        indicators.append('hash_like')
        score += 1.0

    # Sensitivity — lower threshold = more aggressive
    label = 'threat' if score >= 1.0 else 'non-threat'

    # 4️⃣ AI classification via Hugging Face router
    if use_ai and HF_TOKEN:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "inputs": text[:1200],
            "parameters": {
                "candidate_labels": ["cyber threat", "benign", "data breach", "malware attack"],
                "hypothesis_template": "This text is about {}."
            }
        }

        success = False
        for url in HF_API_URLS:
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=60)
                if r.status_code == 200:
                    result = r.json()

                    # ✅ Handle both modern (list) and legacy (dict) outputs
                    if isinstance(result, list) and len(result) > 0 and "label" in result[0]:
                        ai_label = result[0]["label"]
                        ai_score = round(result[0]["score"], 2)
                    elif "labels" in result and "scores" in result:
                        ai_label = result["labels"][0]
                        ai_score = round(result["scores"][0], 2)
                    else:
                        indicators.append(f"AI unexpected response format from {url}: {result}")
                        continue  # Try next endpoint

                    indicators.append(f"AI: {ai_label} ({ai_score})")

                    # Mark as threat if moderately confident
                    if ai_label in ["cyber threat", "data breach", "malware attack"] and ai_score >= 0.45:
                        label = "threat"
                        score += 2.0

                    success = True
                    break
                else:
                    indicators.append(f"AI endpoint {url} returned HTTP {r.status_code}")
            except Exception as e:
                indicators.append(f"AI error with {url}: {e}")

        if not success:
            indicators.append("AI model unavailable or all endpoints failed")

    elif use_ai:
        indicators.append("AI disabled: missing HF token")

    # 🧩 Determine specific threat type
    threat_type = None
    if label == "threat":
        if any(k in t for k in ["phish", "login", "verify", "paypal", "bank"]):
            threat_type = "phishing"
        elif any(k in t for k in ["malware", "virus", "trojan", "worm", "backdoor", "payload"]):
            threat_type = "malware"
        elif any(k in t for k in ["leak", "breach", "dump", "credentials", "pwned"]):
            threat_type = "data breach"
        elif any(k in t for k in ["exploit", "rce", "xss", "injection", "vulnerability"]):
            threat_type = "exploitation"

    # 🏷️ Append the type if detected
    if threat_type:
        label = f"{label} ({threat_type})"
        indicators.insert(0, f"Threat type: {threat_type}")

    return label, round(score, 2), indicators






