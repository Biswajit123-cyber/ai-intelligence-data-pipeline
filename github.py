import aiohttp
from ..http import fetch_text
import json

async def repository_stars(repo_url: str, token: str = "") -> int | None:
    if not repo_url:
        return None
    parts = repo_url.rstrip("/").split("github.com/")
    if len(parts) != 2:
        return None
    owner_repo = parts[1].split("#")[0].split("?")[0]
    if owner_repo.endswith(".git"):
        owner_repo = owner_repo[:-4]
    if owner_repo.count("/") != 1:
        return None

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI-Intelligence-Pipeline/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"https://api.github.com/repos/{owner_repo}"
    async with aiohttp.ClientSession() as session:
        text = await fetch_text(session, url, semaphore=__import__("asyncio").Semaphore(5), headers=headers)
    return json.loads(text).get("stargazers_count")
