import html
import json
import os
import urllib.error
import urllib.request

USERNAME = "jochris"
REPOS = ["JaWa", "Gowa", "LuneBot", "Gorvix"]
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets")

LANG_COLORS = {
    "Go": "#00ADD8",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Python": "#3572A5",
    "Java": "#b07219",
    "Shell": "#89e051",
}

def fetch_url(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status != 200:
                return None
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None

def is_valid_svg(content):
    if not content:
        return False
    low = content.lower()
    if "<svg" not in low:
        return False
    bad_markers = ["something went wrong", "payment required", "deployment_disabled", "could not fetch", "not found", "rate limit"]
    return not any(m in low for m in bad_markers)

def github_api(path):
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    headers = {
        "User-Agent": "jochris-readme-updater",
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    raw = fetch_url(f"https://api.github.com{path}", headers=headers)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None

def render_fallback_pin(repo_name):
    data = github_api(f"/repos/{USERNAME}/{repo_name}")
    if not data:
        return None
    desc = data.get("description") or "No description provided."
    if len(desc) > 58:
        desc = desc[:55] + "..."
    lang = data.get("language") or "Code"
    color = LANG_COLORS.get(lang, "#70a5fd")
    stars = data.get("stargazers_count", 0)
    forks = data.get("forks_count", 0)
    return (
        f'<svg width="400" height="120" viewBox="0 0 400 120" fill="none" xmlns="http://www.w3.org/2000/svg">'
        f'<rect x="0.5" y="0.5" rx="4.5" width="399" height="119" fill="#1a1b27" stroke="#e4e2e2" stroke-opacity="0.2"/>'
        f'<text x="25" y="34" font-family="Segoe UI, Ubuntu, sans-serif" font-size="16" font-weight="600" fill="#70a5fd">{html.escape(repo_name)}</text>'
        f'<text x="25" y="60" font-family="Segoe UI, Ubuntu, sans-serif" font-size="12" fill="#a9b1d6">{html.escape(desc)}</text>'
        f'<circle cx="30" cy="94" r="5" fill="{color}"/>'
        f'<text x="41" y="98" font-family="Segoe UI, Ubuntu, sans-serif" font-size="12" fill="#a9b1d6">{html.escape(lang)}</text>'
        f'<text x="150" y="98" font-family="Segoe UI, Ubuntu, sans-serif" font-size="12" fill="#a9b1d6">Stars: {stars}</text>'
        f'<text x="240" y="98" font-family="Segoe UI, Ubuntu, sans-serif" font-size="12" fill="#a9b1d6">Forks: {forks}</text>'
        f'</svg>'
    )

def render_fallback_stats():
    user = github_api(f"/users/{USERNAME}")
    repos = github_api(f"/users/{USERNAME}/repos?per_page=100")
    if not user or not isinstance(repos, list):
        return None
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    public_repos = user.get("public_repos", len(repos))
    followers = user.get("followers", 0)
    name = user.get("name") or USERNAME
    return (
        f'<svg width="467" height="195" viewBox="0 0 467 195" fill="none" xmlns="http://www.w3.org/2000/svg">'
        f'<rect x="0.5" y="0.5" rx="4.5" width="466" height="194" fill="#1a1b27"/>'
        f'<text x="25" y="35" font-family="Segoe UI, Ubuntu, sans-serif" font-size="18" font-weight="600" fill="#70a5fd">{html.escape(name)}\'s GitHub Stats</text>'
        f'<text x="25" y="72" font-family="Segoe UI, Ubuntu, sans-serif" font-size="14" font-weight="600" fill="#a9b1d6">Total Stars Earned:</text>'
        f'<text x="220" y="72" font-family="Segoe UI, Ubuntu, sans-serif" font-size="14" font-weight="700" fill="#bf91f3">{total_stars}</text>'
        f'<text x="25" y="100" font-family="Segoe UI, Ubuntu, sans-serif" font-size="14" font-weight="600" fill="#a9b1d6">Public Repositories:</text>'
        f'<text x="220" y="100" font-family="Segoe UI, Ubuntu, sans-serif" font-size="14" font-weight="700" fill="#bf91f3">{public_repos}</text>'
        f'<text x="25" y="128" font-family="Segoe UI, Ubuntu, sans-serif" font-size="14" font-weight="600" fill="#a9b1d6">Total Forks:</text>'
        f'<text x="220" y="128" font-family="Segoe UI, Ubuntu, sans-serif" font-size="14" font-weight="700" fill="#bf91f3">{total_forks}</text>'
        f'<text x="25" y="156" font-family="Segoe UI, Ubuntu, sans-serif" font-size="14" font-weight="600" fill="#a9b1d6">Followers:</text>'
        f'<text x="220" y="156" font-family="Segoe UI, Ubuntu, sans-serif" font-size="14" font-weight="700" fill="#bf91f3">{followers}</text>'
        f'</svg>'
    )

def save_svg(filename, primary_url, fallback_fn):
    svg = fetch_url(primary_url)
    if not is_valid_svg(svg):
        svg = fallback_fn()
    if is_valid_svg(svg):
        dest = os.path.join(ASSETS_DIR, filename)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"updated {filename}")
    else:
        print(f"kept existing {filename}")

def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    save_svg(
        "stats.svg",
        f"https://github-stats-extended.vercel.app/api?username={USERNAME}&show_icons=true&include_all_commits=true&theme=tokyonight&hide_border=true",
        render_fallback_stats,
    )
    for repo in REPOS:
        save_svg(
            f"pin-{repo}.svg",
            f"https://github-stats-extended.vercel.app/api/pin/?username={USERNAME}&repo={repo}&theme=tokyonight",
            lambda r=repo: render_fallback_pin(r),
        )

if __name__ == "__main__":
    main()
