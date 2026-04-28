# hedgehog-seo-auditor

FastMCP server that wraps the [Agentic-SEO-Skill](https://github.com/Bhanunamikaze/Agentic-SEO-Skill) scripts as MCP tools. Designed to be called from Claude.ai chat, NHH (Nearly Headless Hilda), and Claude Code during client SEO audits.

## What it does

Exposes 13 MCP tools covering every major SEO audit type:

| Tool | What it checks |
|---|---|
| `seo_technical_audit` | Robots.txt, redirects, canonicals, security headers |
| `seo_content_quality` | Keyword optimisation, readability, entity coverage |
| `seo_schema_audit` | JSON-LD / structured data validity |
| `seo_pagespeed` | Core Web Vitals via PageSpeed Insights API |
| `seo_links` | Internal links, link profile, broken links |
| `seo_sitemap` | Sitemap URL accessibility |
| `seo_geo_readiness` | llms.txt, robots AI directives, GEO signals |
| `seo_hreflang` | International SEO hreflang correctness |
| `seo_duplicate_content` | Near-duplicate pages, missing canonicals |
| `seo_competitor_gap` | Keyword/content gap vs a competitor domain |
| `seo_indexnow` | IndexNow submission for rapid re-indexing |
| `seo_images` | Alt text, dimensions, lazy-loading signals |
| `seo_full_audit` | All core checks in one call (60–90s) |

Claude synthesises the returned findings dict into a report using the `hilda-agent-reporting` skill.

## Local setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy env vars
cp .env.example .env
# Fill in PAGESPEED_API_KEY at minimum

# 3. Run the server
python server.py
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `PAGESPEED_API_KEY` | Yes (for `seo_pagespeed`) | Google PageSpeed Insights API key |
| `INDEXNOW_KEY` | Yes (for `seo_indexnow`) | IndexNow API key for the target domain |

## Optional: Playwright (screenshot tools)

`seo_visual` and `seo_screenshot` are not implemented — they require Playwright and break lean deploys. To add them locally:

```bash
pip install playwright
playwright install chromium
```

## Deploy to Fly.io

```bash
fly auth login
fly launch --name hedgehog-seo-auditor --region syd
fly secrets set PAGESPEED_API_KEY=your_key_here
fly deploy
```

## Add to Claude.ai as MCP server

Once deployed, add to Claude.ai → Settings → Integrations:
- **URL:** `https://hedgehog-seo-auditor.fly.dev`
- **Transport:** HTTP

## Notes

- Scripts in `scripts/` are upstream from Agentic-SEO-Skill — do not modify them
- `seo_gsc` (Google Search Console) is out of scope — requires per-client OAuth
- `seo_full_audit` can take 60–90 seconds; inform Claude of this in your prompt if needed
