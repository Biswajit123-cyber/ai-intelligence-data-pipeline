# AI Intelligence Data Pipeline

Production-oriented demo implementation for the GraphOne / FrontierAtlas AI Engineer assignment.

## What this project implements

- Async HTTP ingestion with `asyncio` + `aiohttp`
- Research-paper ingestion from arXiv
- GitHub repository discovery and current star metrics
- Configurable startup/product/news/job source adapters
- 24-hour freshness filtering for news and jobs
- Date normalization for ISO, RSS/HTML metadata and relative dates
- LLM extraction with a multi-provider fallback chain
- Intelligent text chunking to avoid oversized requests
- Exponential backoff + jitter for HTTP 429/5xx and provider failures
- Deterministic entity resolution using normalization, aliases and fuzzy matching
- Source URL provenance on every record
- SQLite storage for the demo, with PostgreSQL/Redis architecture described in `architecture.md`
- JSON/CSV exports matching the six requested output tabs
- Unit tests for date parsing, entity resolution and chunking

## Important data-integrity rule

The pipeline never fabricates source URLs or extracted facts. Records are created only from fetched source content/API responses. If an LLM cannot confidently extract a field, the field remains null.

The assignment explicitly warns that hallucinated data can cause disqualification.

## Quick start

### 1. Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env` and add keys only for providers you intend to use.

### 4. Run a safe demo

```bash
python -m src.main demo
```

This exercises the pipeline without claiming that demo records satisfy the 1,000-row submission requirement.

### 5. Run research-paper ingestion

```bash
python -m src.main papers --query "artificial intelligence" --limit 1000
```

The arXiv API supplies paper metadata programmatically. GitHub metrics are fetched through GitHub's public REST API when a repository can be identified.

### 6. Run exports

```bash
python -m src.main export
```

Files are written to `data/exports/`.

## LLM extraction

The provider interface is deliberately isolated in `src/llm/orchestrator.py`.

Recommended provider order:

1. Gemini
2. Groq
3. DeepSeek

The orchestrator:
- validates structured JSON
- chunks oversized text
- retries transient failures
- waits using exponential backoff with jitter
- falls through to the next provider after repeated failure

## Scaling to 500k+

The code uses bounded concurrency rather than creating an unbounded task for every URL. At production scale, the same worker logic can be run behind a queue such as Kafka/SQS/RabbitMQ, with Redis for deduplication/rate-limit state and PostgreSQL for canonical entities and provenance.

No crawler should attempt to defeat CAPTCHA or access controls. For heavily protected domains, the production strategy is API/RSS/feed acquisition, licensed data, browser automation only where permitted, or a human-approved connector.

## Deliverables

The generated exports correspond to:

- Startups
- Products
- Research Papers
- Jobs
- News
- Entity Mapping Log

See `architecture.md` for the technical design and `architecture.pdf` for a submission-ready version.
