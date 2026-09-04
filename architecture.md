# AI Intelligence Pipeline Architecture

## 1. Goal

Build a fault-tolerant ingestion system that can grow from a demo to 500,000+ startup, product and research-paper records without changing worker logic.

## 2. Logical flow

```text
                +-------------------+
                | Source Registry   |
                +---------+---------+
                          |
             +------------+------------+
             |                         |
       Async Crawlers             API Clients
             |                         |
             +------------+------------+
                          |
                    Raw Fetch Layer
                          |
                  Content Extraction
                          |
              +-----------+-----------+
              |                       |
        Date/Freshness           Dedup Key
        validation              URL/hash
              |                       |
              +-----------+-----------+
                          |
                    LLM Extractor
                Gemini -> Groq -> DeepSeek
                          |
                  Schema Validation
                          |
                   Entity Resolver
                          |
             +------------+-------------+
             |                          |
        PostgreSQL                 Vector/Graph
       canonical data              relationships
             |                          |
             +------------+-------------+
                          |
                    Export / Sheets
```

## 3. Scale strategy

At 500k+ records, the crawler should be queue-driven.

- Scheduler creates URL/API work items.
- Kafka/SQS/RabbitMQ distributes jobs.
- Workers use bounded async concurrency.
- Redis stores short-lived deduplication keys, leases and rate-limit state.
- PostgreSQL stores canonical entities, source provenance and processing status.
- Object storage keeps raw HTML/JSON snapshots.
- A graph store can model Startup -> Founder -> Product -> Paper -> Repository relationships.
- Horizontal scaling means adding workers, not rewriting crawler logic.

A practical partition key is source + URL hash. This avoids two workers processing the same URL simultaneously.

## 4. 413 handling

413 means the request payload is too large.

The LLM layer first normalizes HTML to clean text, removes boilerplate, then applies bounded semantic chunks. Each chunk has a hard character budget. If a provider still rejects the request, the budget is reduced and the provider fallback is attempted.

Do not blindly truncate from the beginning. Preserve title, headings, metadata and high-density paragraphs first.

## 5. 429 handling

For rate limiting:

1. Read `Retry-After` when available.
2. Otherwise use exponential backoff: `2^attempt + random_jitter`.
3. Cap the delay.
4. Limit concurrency per provider.
5. Track provider health.
6. Fail over to the next provider after the configured retry budget.

This prevents a thundering herd when many workers receive 429 responses together.

## 6. Freshness and deduplication

For news/jobs, compute:

`dedup_key = SHA256(normalized_url + normalized_title)`

Store the key with source and first-seen timestamp.

Freshness check:

`0 <= now - published_at <= 24 hours`

Date extraction order:

1. JSON-LD `datePublished`
2. OpenGraph/article metadata
3. RSS/Atom published/updated field
4. Visible page date
5. Relative date parser
6. Last-seen heuristic only when strict publication time is unavailable

If publication time cannot be established with sufficient confidence, do not claim the item is 24-hour fresh.

## 7. Entity resolution

Resolution order:

1. Exact normalized name
2. Alias table
3. Deterministic cleanup of legal suffixes
4. Fuzzy match above a conservative threshold
5. Unresolved queue for review

Example:

`Open AI` -> `OpenAI`

`OpenAI, Inc.` -> `OpenAI`

Every mapping is logged with raw name, canonical name, method and score.

## 8. Anti-bot strategy

The objective is resilient acquisition, not bypassing security controls.

Preferred order:

1. Official API
2. RSS/Atom feed
3. Licensed/authorized data source
4. Normal HTTP crawling where permitted
5. Playwright for JavaScript-rendered pages where automation is permitted
6. Human/manual review for CAPTCHA or access-control challenges

Do not automate CAPTCHA solving or attempt to defeat Cloudflare/Datadome controls. In production, protected sources should be handled through an approved integration or licensed feed.

## 9. Storage

### Demo

SQLite is sufficient for local development and interview demonstration.

### Production

PostgreSQL:
- canonical startups/products
- source records
- processing state
- entity mappings

Object storage:
- raw HTML/JSON
- crawl snapshots

Redis:
- distributed locks
- URL deduplication
- provider rate-limit state

Graph database:
- relationships such as Startup-FOUNDED_BY-Founder, Startup-HAS_PRODUCT-Product, Paper-IMPLEMENTED_BY-Repository

Vector database:
- semantic similarity and entity candidate retrieval.

## 10. Observability

Every worker should emit structured logs with:

- job_id
- source
- URL
- status
- HTTP status
- retry count
- provider
- latency
- extracted record count
- validation errors

Metrics:

- requests/minute
- success rate
- 429 rate
- 413 rate
- freshness pass rate
- extraction validation rate
- duplicate rate
- provider fallback rate
