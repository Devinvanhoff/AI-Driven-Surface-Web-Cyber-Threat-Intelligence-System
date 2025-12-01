import requests

def check_email_pwned(email):
    """
    Returns True if email found in known breaches, False otherwise.
    Uses the Have I Been Pwned public API (no API key needed).
    """
    try:
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {
            "User-Agent": "SurfaceSentinelStudentProject",
            "hibp-api-key": ""  # leave empty for public test endpoints
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return True
        elif resp.status_code == 404:
            return False
        else:
            return None  # rate-limited or unknown error
    except Exception as e:
        print("HIBP error:", e)
        return None
