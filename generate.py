import urllib.request
import urllib.error
import json
import os
import sys
from datetime import datetime, timezone, timedelta

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not set")
    sys.exit(1)

# Pacific time (UTC-7 during daylight saving)
pacific_offset = timedelta(hours=-7)
now = datetime.now(timezone.utc) + pacific_offset
today_str = now.strftime("%A, %B %-d, %Y")

# Iran war day count (started Feb 28, 2026)
war_start = datetime(2026, 2, 28)
war_day = (now.replace(tzinfo=None) - war_start).days + 1

print("Generating brief for " + today_str + " (Iran war day " + str(war_day) + ")")

iran_tag = "iran war - day " + str(war_day)

prompt = """Today is """ + today_str + """. Search the web for today's news, then return ONLY a JSON object. No markdown, no backticks, no explanation. Start your response with { and end with }.

Search for: top news """ + today_str + """, Iran war update today, US politics today, stock market today, gas prices today, pop culture entertainment news this week, trending TikTok or meme right now.

Return this exact JSON structure filled with real current data:

{
  "date": \"""" + today_str + """\",
  "headlines": [
    {"text": "real headline 1", "tag": "emoji"},
    {"text": "real headline 2", "tag": "emoji"},
    {"text": "real headline 3", "tag": "emoji"},
    {"text": "real headline 4", "tag": "emoji"},
    {"text": "real headline 5", "tag": "emoji"},
    {"text": "real headline 6", "tag": "emoji"},
    {"text": "real headline 7", "tag": "emoji"},
    {"text": "real headline 8", "tag": "emoji"},
    {"text": "real headline 9", "tag": "emoji"},
    {"text": "real headline 10", "tag": "emoji"}
  ],
  "breaking": {"show": false, "text": "", "url": ""},
  "stories": [
    {"tag": \"""" + iran_tag + """\", "tagType": "fire", "hed": "Iran war headline today", "dek": "2-3 funny accurate sentences.", "url": "real url", "source": "outlet", "chips": ["chip1", "chip2"]},
    {"tag": "international", "tagType": "geo", "hed": "real headline", "dek": "real dek", "url": "real url", "source": "outlet", "chips": []},
    {"tag": "domestic", "tagType": "us", "hed": "real headline", "dek": "real dek", "url": "real url", "source": "outlet", "chips": []},
    {"tag": "domestic", "tagType": "us", "hed": "real headline", "dek": "real dek", "url": "real url", "source": "outlet", "chips": []},
    {"tag": "spicy take", "tagType": "spicy", "hed": "real headline", "dek": "real dek", "url": "real url", "source": "outlet", "chips": []}
  ],
  "markets": {
    "sp500": {"val": "0,000", "chg": "+0.0%", "dir": "up"},
    "dow": {"val": "00,000", "chg": "+0.0%", "dir": "up"},
    "nasdaq": {"val": "00,000", "chg": "+0.0%", "dir": "up"},
    "wti": {"val": "$00", "chg": "-0%", "dir": "down"},
    "brent": {"val": "$00", "chg": "-0%", "dir": "down"},
    "gold": {"val": "$0,000", "chg": "+0%", "dir": "up"},
    "btc": {"val": "$00,000", "chg": "+0%", "dir": "up"},
    "context": "one sentence why markets moved today",
    "url": "https://cnbc.com",
    "source": "CNBC"
  },
  "gas": {
    "avg": "$0.00",
    "note": "funny one-liner about gas prices",
    "premium": "$0.00",
    "wti": "$00",
    "highState": "CA: $0.00",
    "lowState": "OK: $0.00",
    "url": "https://gasprices.aaa.com",
    "source": "AAA"
  },
  "popCulture": {
    "hed": "real entertainment headline from this week only",
    "dek": "two fun sentences",
    "url": "real url",
    "source": "outlet"
  },
  "genZ": {
    "type": "tiktok OR meme OR viral OR celeb OR trending — pick whichever fits best",
    "term": "the specific name of the thing — a meme, a viral moment, a celebrity drama, a TikTok audio, a tweet, whatever is actually being talked about TODAY",
    "definition": "what it is and why everyone is talking about it, 2 sentences. Must be something that happened or went viral THIS WEEK. Do NOT use generic slang words like delulu, brain rot, rizz, etc.",
    "usage": "funny example sentence connecting it to today's news or current events",
    "url": "",
    "source": ""
  },
  "tldr": "two sentence summary of today"
}

Rules: fill ALL placeholder values with real data from your search. Real URLs only. Dry wit. No HTML in strings. Pop culture max 7 days old. Market numbers must be actual current values."""

payload = {
    "model": "claude-sonnet-4-6",
    "max_tokens": 2500,
    "tools": [{"type": "web_search_20250305", "name": "web_search"}],
    "messages": [{"role": "user", "content": prompt}]
}

req = urllib.request.Request(
    "https://api.anthropic.com/v1/messages",
    data=json.dumps(payload).encode(),
    headers={
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print("HTTP Error " + str(e.code) + ": " + body)
    sys.exit(1)

text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
if not text_blocks:
    print("ERROR: No text in response")
    print(json.dumps(data, indent=2))
    sys.exit(1)

raw = " ".join(text_blocks)
raw = raw.replace("```json", "").replace("```", "").strip()

start = raw.index("{")
end = raw.rindex("}") + 1
brief = json.loads(raw[start:end])

with open("brief-data.json", "w") as f:
    json.dump(brief, f, indent=2, ensure_ascii=False)

print("SUCCESS: Brief generated for " + today_str)
