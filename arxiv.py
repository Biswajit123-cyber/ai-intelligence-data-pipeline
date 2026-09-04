import asyncio
import xml.etree.ElementTree as ET
import aiohttp
from datetime import datetime, timezone
from ..models import ResearchPaper
from ..http import fetch_text

ARXIV_NS = {"a": "http://www.w3.org/2005/Atom"}

async def fetch_arxiv(query: str, limit: int, github_token: str = "") -> list[ResearchPaper]:
    url = (
        "https://export.arxiv.org/api/query?"
        f"search_query=all:{query.replace(' ', '+')}&start=0&max_results={limit}"
    )
    sem = asyncio.Semaphore(5)
    headers = {"User-Agent": "AI-Intelligence-Pipeline/1.0 research-demo"}
    async with aiohttp.ClientSession() as session:
        xml = await fetch_text(session, url, semaphore=sem, headers=headers)
    root = ET.fromstring(xml)

    papers = []
    for entry in root.findall("a:entry", ARXIV_NS):
        title = (entry.findtext("a:title", default="", namespaces=ARXIV_NS) or "").strip()
        paper_url = (entry.findtext("a:id", default="", namespaces=ARXIV_NS) or "").strip()
        published = (entry.findtext("a:published", default="", namespaces=ARXIV_NS) or "").strip()
        authors = [
            (x.findtext("a:name", default="", namespaces=ARXIV_NS) or "").strip()
            for x in entry.findall("a:author", ARXIV_NS)
        ]
        papers.append(
            ResearchPaper(
                source={"name": "arXiv", "url": paper_url},
                content={
                    "title": title,
                    "authors": authors,
                    "paper_url": paper_url,
                    "github_url": None,
                    "github_stars": None,
                    "published_date": published,
                },
                collectedAt=datetime.now(timezone.utc),
            )
        )
    return papers
