# World Cup Newsletter

A beginner-friendly Python script that fetches the previous day's World Cup match results, asks Claude to write a friendly recap, and emails it to you. Can be scheduled to run automatically every day.

## What it does

1. Fetches yesterday's World Cup fixtures and scores from [api-football.com](https://www.api-football.com/)
2. Sends the results to the Claude API, which writes a short, casual recap
3. Emails the recap (plus the full scoreline list) to you via Gmail

## Requirements

- Python 3.9+
- An [api-football.com](https://www.api-football.com/) account (free tier works)
- An [Anthropic API key](https://console.anthropic.com/)
- A Gmail account with an **App Password** (not your normal password)

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/stevsvc1997/WorldCupNewsletter.git
cd WorldCupNewsletter
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

This installs:
- `requests` — for calling the api-football and Anthropic APIs
- `python-dotenv` — for loading your secret keys from a `.env` file

**3. Set up your API keys**

Copy the example env file:
```bash
cp .env.example .env
```

Then open `.env` and fill in your real values:
```
API_FOOTBALL_KEY=your_api_football_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GMAIL_ADDRESS=youraddress@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
RECIPIENT_EMAIL=youraddress@gmail.com
```

> ⚠️ Never commit `.env` to git — it's already listed in `.gitignore` so this should happen automatically.

**Getting each key:**
- **api-football.com**: sign up free at their site, key is on your dashboard
- **Anthropic**: sign up at console.anthropic.com, create a key under Settings → API Keys (new accounts get free starter credit, no card required)
- **Gmail App Password**: turn on 2-Step Verification at `myaccount.google.com/security`, then generate a password at `myaccount.google.com/apppasswords`

**4. Run it**
```bash
python world_cup_newsletter.py
```

If everything is set up correctly, you'll see `Newsletter sent!` and an email will land in your inbox shortly after.

## Scheduling (run it automatically every day)

**Mac/Linux (cron):**
```bash
crontab -e
```
Add this line to run it every day at 8:00 AM:
```
0 8 * * * /usr/bin/python3 /full/path/to/world_cup_newsletter.py
```

**Windows:**
Use Task Scheduler → "Create Basic Task" → Daily → point it at `python.exe` with this script as the argument.

## Notes

- Costs are minimal: one Claude API call and one api-football call per run, well within free-tier limits for daily use.
- `RECIPIENT_EMAIL` can be a phone carrier's email-to-SMS gateway (e.g. `yournumber@txt.att.net`) if you'd rather get a text than an email.
