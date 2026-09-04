import argparse
import asyncio
from datetime import datetime, timezone
from .config import settings, EXPORT_DIR
from .sources.arxiv import fetch_arxiv
from .storage import write_json, write_csv
from .entity_resolver import EntityResolver

def demo():
    resolver = EntityResolver(["OpenAI", "Anthropic", "Google DeepMind", "Microsoft"])
    examples = ["Open AI", "OpenAI, Inc.", "Anthropic", "Google DeepMind"]
    for x in examples:
        print(resolver.resolve(x, "STARTUP").model_dump())

async def papers(query: str, limit: int):
    records = await fetch_arxiv(query, limit, settings.github_token)
    write_json(records, EXPORT_DIR / "research_papers.json")
    write_csv(records, EXPORT_DIR / "research_papers.csv")
    print(f"Fetched {len(records)} arXiv records")

def export():
    print(f"Exports directory: {EXPORT_DIR}")

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("demo")

    p = sub.add_parser("papers")
    p.add_argument("--query", default="artificial intelligence")
    p.add_argument("--limit", type=int, default=100)

    sub.add_parser("export")
    args = parser.parse_args()

    if args.command == "demo":
        demo()
    elif args.command == "papers":
        asyncio.run(papers(args.query, args.limit))
    elif args.command == "export":
        export()

if __name__ == "__main__":
    main()
