"""
World Cup Daily Newsletter
---------------------------
A beginner-friendly script that:
  1. Fetches yesterday's World Cup match results + stats
  2. Asks Claude to write a friendly recap
  3. Emails it to you

SETUP (one-time):
  1. Sign up free at https://www.api-football.com/  -> get an API key
  2. Get an Anthropic API key from https://console.anthropic.com/
  3. Turn on Gmail "App Passwords": https://myaccount.google.com/apppasswords
     (you need 2FA enabled on your Google account first)
  4. Install dependencies:  pip install requests python-dotenv
  5. Copy .env.example to a new file named .env, and fill in your real keys
     (never commit .env to git -- it's already in .gitignore)
  6. Run:  python world_cup_newsletter.py

SCHEDULING (run it automatically every day):
  Mac/Linux (cron):
    1. Run:  crontab -e
    2. Add this line (runs every day at 8:00 AM):
       0 8 * * * /usr/bin/python3 /full/path/to/world_cup_newsletter.py

  Windows:
    Use Task Scheduler -> "Create Basic Task" -> Daily -> point it at
    python.exe with this script as the argument.
"""

import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ---------------- CONFIG ----------------
# Secrets are loaded from a local .env file (never committed to git).
# See .env.example for the template.
load_dotenv()

API_FOOTBALL_KEY = os.environ["API_FOOTBALL_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", GMAIL_ADDRESS)

WORLD_CUP_LEAGUE_ID = 1   # World Cup league id on api-football.com (verify in their docs)
# -----------------------------------------


def get_yesterdays_matches():
    """Fetch yesterday's World Cup fixtures + scores from api-football.com"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    params = {"league": WORLD_CUP_LEAGUE_ID, "season": 2026, "date": yesterday}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if data.get("errors"):
        print("API returned an error:", data["errors"])

    matches = []
    for fixture in data.get("response", []):
        teams = fixture["teams"]
        goals = fixture["goals"]
        matches.append({
            "home": teams["home"]["name"],
            "away": teams["away"]["name"],
            "home_score": goals["home"],
            "away_score": goals["away"],
        })
    return matches


def get_match_statistics(fixture_id):
    """Optional: pull deeper stats (possession, shots, etc.) for one match"""
    url = "https://v3.football.api-sports.io/fixtures/statistics"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    params = {"fixture": fixture_id}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("response", [])


def write_recap_with_claude(matches):
    """Send the raw match data to Claude and get back a friendly recap"""
    if not matches:
        return "No World Cup matches were played yesterday."

    match_lines = "\n".join(
        f"- {m['home']} {m['home_score']} - {m['away_score']} {m['away']}"
        for m in matches
    )

    prompt = f"""Here are yesterday's World Cup results:
{match_lines}

Write a short, friendly newsletter recap (3-5 sentences) highlighting the
most interesting results, any upsets, and high-scoring games. Keep it casual
and fun to read."""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    response.raise_for_status()
    content = response.json()["content"]
    return "".join(block["text"] for block in content if block["type"] == "text")


def send_email(subject, body):
    """Send the newsletter via Gmail"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(msg)


def main():
    matches = get_yesterdays_matches()
    recap = write_recap_with_claude(matches)

    # Build the email body: AI recap + raw scoreline list
    scoreline_text = "\n".join(
        f"{m['home']} {m['home_score']} - {m['away_score']} {m['away']}"
        for m in matches
    ) or "No matches yesterday."

    body = f"{recap}\n\n---\nFull scores:\n{scoreline_text}"
    date_str = (datetime.now() - timedelta(days=1)).strftime("%B %d, %Y")

    send_email(subject=f"World Cup Recap - {date_str}", body=body)
    print("Newsletter sent!")


if __name__ == "__main__":
    main()