import asyncio
from datetime import datetime, timezone
import feedparser
import aiohttp
from bs4 import BeautifulSoup
from ..date_utils import normalize_datetime, is_fresh_24h
from ..http import fetch_text
from ..models import News, Job

async def ingest_feed(feed_url: str, source_name: str, kind: str) -> list:
    parsed = await asyncio.to_thread(feedparser.parse, feed_url)
    now = datetime.now(timezone.utc)
    out = []

    for item in parsed.entries:
        raw_date = item.get("published") or item.get("updated") or item.get("created")
        dt = normalize_datetime(raw_date, now)
        if not dt or not is_fresh_24h(dt, now):
            continue

        link = item.get("link")
        title = item.get("title", "").strip()
        summary = BeautifulSoup(item.get("summary", ""), "html.parser").get_text(" ", strip=True)

        if kind == "news":
            out.append(News(
                source={"name": source_name, "url": link},
                content={
                    "title": title,
                    "url": link,
                    "date": dt.isoformat(),
                    "full_text": summary,
                },
                collectedAt=now,
            ))
        else:
            out.append(Job(
                source={"name": source_name, "url": link},
                content={
                    "company": None,
                    "title": title,
                    "url": link,
                    "date": dt.isoformat(),
                    "is_remote": None,
                    "role_family": None,
                },
                collectedAt=now,
            ))
    return out
