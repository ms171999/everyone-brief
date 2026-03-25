[README.md](https://github.com/user-attachments/files/26252650/README.md)
# Everyone · Daily Brief

A daily news brief for the group chat, powered by Claude.

## One-time setup

1. Push this repo to GitHub
2. Connect Netlify to this GitHub repo (Site configuration → Build & deploy → Link to Git)
3. Netlify will auto-deploy every time `index.html` changes

## Daily update (2 min)

Ask Claude: **"Update my everyone brief GitHub file for today"**

Claude will:
- Search today's news
- Generate fresh JSON
- Edit `brief-data.json` in this repo via the GitHub API
- Netlify auto-deploys in ~15 seconds

## Files

- `index.html` — the site (never needs to change)
- `brief-data.json` — today's brief data (updated daily)
