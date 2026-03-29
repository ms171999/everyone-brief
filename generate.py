import urllib.request
import urllib.error
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta

def call_api(payload, api_key, max_retries=3):
    for attempt in range(max_retries):
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
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if e.code == 429:
                wait = 65 * (attempt + 1)
                print("Rate limited. Waiting " + str(wait) + "s before retry " + str(attempt + 1) + "/" + str(max_retries))
                time.sleep(wait)
            else:
                print("HTTP Error " + str(e.code) + ": " + body)
                sys.exit(1)
    print("ERROR: Max retries exceeded")
    sys.exit(1)

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not set")
    sys.exit(1)

pacific_offset = timedelta(hours=-7)
now = datetime.now(timezone.utc) + pacific_offset
today_str = now.strftime("%A, %B %-d, %Y")

war_start = datetime(2026, 2, 28)
war_day = (now.replace(tzinfo=None) - war_start).days + 1
iran_tag = "iran war - day " + str(war_day)

print("Generating brief for " + today_str + " (Iran war day " + str(war_day) + ")")

prompt = """Today is """ + today_str + """. Search the web for today's news, then return ONLY a JSON object. No markdown, no backticks, no explanation. Start your response with { and end with }. Use only straight ASCII quotes.

Search for: top news """ + today_str + """, Iran war update today, US politics today, stock market today, gas prices today, pop culture entertainment news this week, trending viral moment or meme right now.

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
    "type": "meme OR tiktok OR viral OR celeb",
    "term": "specific name of whatever is actually going viral this week",
    "definition": "what it is and why everyone is talking about it, 2 sentences. Must be from this week. Not basic slang.",
    "usage": "funny example applying it to today's news",
    "url": "",
    "source": ""
  },
  "tldr": "two sentence summary of today"
}

Rules: real URLs only, dry wit, no HTML in strings, pop culture max 7 days old, fill all market numbers with actual values."""

payload = {
    "model": "claude-sonnet-4-6",
    "max_tokens": 2500,
    "tools": [{"type": "web_search_20250305", "name": "web_search"}],
    "messages": [{"role": "user", "content": prompt}]
}

data = call_api(payload, api_key)

text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
if not text_blocks:
    print("ERROR: No text in response")
    print(json.dumps(data, indent=2))
    sys.exit(1)

raw = " ".join(text_blocks)
raw = raw.replace("```json", "").replace("```", "").strip()

start = raw.index("{")
end = raw.rindex("}") + 1
json_str = raw[start:end]

import re
json_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', json_str)
json_str = json_str.replace('\u2018', "'").replace('\u2019', "'")
json_str = json_str.replace('\u201c', '"').replace('\u201d', '"')

try:
    brief = json.loads(json_str)
except json.JSONDecodeError as e:
    print("Parse failed: " + str(e))
    char = e.pos
    print("Context: " + repr(json_str[max(0,char-100):char+100]))
    sys.exit(1)

with open("brief-data.json", "w") as f:
    json.dump(brief, f, indent=2, ensure_ascii=False)

print("SUCCESS: Brief generated for " + today_str)
