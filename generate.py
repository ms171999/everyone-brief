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

print(f"Generating brief for {today_str} (Iran war day {war_day})")

prompt = (
    f"Today is {today_str}. Search the web for today's news, then return ONLY a JSON object "
    "(no markdown, no backticks, start with {, end with }).\n\n"
    f"Search for: top news {today_str}, Iran war today, US politics today, "
    "stock market today, gas prices today, pop culture news this week, trending gen z word or meme.\n\n"
    "Return this JSON structure with real current data:\n"
    "{\n"
    f'  "date": "{today_str}",\n'
    '  "headlines": [10 objects with {"text": "headline", "tag": "emoji"}],\n'
    '  "breaking": {"show": false, "text": "", "url": ""},\n'
    '  "stories": [\n'
    f'    {{"tag": "iran war · day {war_day}", "tagType": "fire", "hed": "...", "dek": "...", "url": "...", "source": "...", "chips": []}},\n'
    '    {"tag": "international", "tagType": "geo", "hed": "...", "dek": "...", "url": "...", "source": "...", "chips": []},\n'
    '    {"tag": "domestic", "tagType": "us", "hed": "...", "dek": "...", "url": "...", "source": "...", "chips": []},\n'
    '    {"tag": "domestic", "tagType": "us", "hed": "...", "dek": "...", "url": "...", "source": "...", "chips": []},\n'
    '    {"tag": "spicy take", "tagType": "spicy", "hed": "...", "dek": "...", "url": "...", "source": "...", "chips": []}\n'
    '  ],\n'
    '  "markets": {\n'
    '    "sp500": {"val": "0,000", "chg": "+0.0%", "dir": "up"},\n'
    '    "dow": {"val": "00,000", "chg": "+0.0%", "dir": "up"},\n'
    '    "nasdaq": {"val": "00,000", "chg": "+0.0%", "dir": "up"},\n'
    '    "wti": {"val": "$00", "chg": "-0%", "dir": "down"},\n'
    '    "brent": {"val": "$00", "chg": "-0%", "dir": "down"},\n'
    '    "gold": {"val": "$0,000", "chg": "+0%", "dir": "up"},\n'
    '    "btc": {"val": "$00,000", "chg": "+0%", "dir": "up"},\n'
    '    "context": "one sentence why markets moved", "url": "https://cnbc.com", "source": "CNBC"\n'
    '  },\n'
    '  "gas": {"avg": "$0.00", "note": "funny one-liner", "premium": "$0.00", "wti": "$00", "highState": "CA: $0.00", "lowState": "OK: $0.00", "url": "https://gasprices.aaa.com", "source": "AAA"},\n'
    '  "popCulture": {"hed": "...", "dek": "...", "url": "...", "source": "..."},\n'
    '  "genZ": {"type": "meme or tiktok — NOT a common slang word everyone already knows", "term": "actual name of the meme/trend", "definition": "what it is and why it's funny, 2 sentences", "usage": "funny example of it applied to today's news or real life", "url": "", "source": ""},\n'
    '  "tldr": "two sentence summary"\n'
    "}\n\n"
    "Rules: use real URLs from search results, dry wit, no HTML in strings, "
    "pop culture must be from this week, fill all market numbers with actual values, "
    "for genZ pick a specific TRENDING TIKTOK or MEME (not basic slang like 'delulu' or 'brain rot' that everyone already knows) — "
    "something actually circulating on TikTok or Twitter/X right now like a specific audio, format, or meme character."
)

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
    print(f"HTTP Error {e.code}: {body}")
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

print(f"SUCCESS: Brief generated for {today_str}")
