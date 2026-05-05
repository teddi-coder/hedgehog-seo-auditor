from fastmcp import FastMCP
import subprocess, json, sys, os

mcp = FastMCP("hedgehog-seo-auditor")

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")


def run_script(script_name: str, args: list[str]) -> dict:
    """Run a script from scripts/ with --json flag. Return parsed JSON or error dict."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    cmd = [sys.executable, script_path] + args + ["--json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return {"error": result.stderr.strip() or f"{script_name} exited with code {result.returncode}"}
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {"error": f"{script_name} timed out after 60s"}
    except json.JSONDecodeError:
        return {"raw_output": result.stdout.strip()}


@mcp.tool()
def seo_technical_audit(url: str) -> dict:
    """
    Run a technical SEO audit on a domain or URL.
    Checks robots.txt, crawlability, canonical tags, redirect chains, and security headers.
    Returns a findings dict with severity labels (critical/warning/pass) for each check.

    Args:
        url: The domain or URL to audit (e.g. 'https://example.com')
    """
    return {
        "robots_checker": run_script("robots_checker.py", [url]),
        "security_headers": run_script("security_headers.py", [url]),
        "redirect_checker": run_script("redirect_checker.py", [url]),
        "parse_html": run_script("parse_html.py", [url]),
    }


@mcp.tool()
def seo_content_quality(url: str) -> dict:
    """
    Audit content quality for SEO on a page or domain.
    Analyses keyword optimisation, readability scores, and entity coverage.
    Returns findings on content gaps, heading structure, and NLP entity signals.

    Args:
        url: The page or domain URL to audit (e.g. 'https://example.com/blog/post')
    """
    return {
        "article_seo": run_script("article_seo.py", [url]),
        "readability": run_script("readability.py", [url]),
        "entity_checker": run_script("entity_checker.py", [url]),
    }


@mcp.tool()
def seo_schema_audit(url: str) -> dict:
    """
    Audit structured data (schema.org) on a page or domain.
    Parses raw HTML for JSON-LD and microdata, then validates against schema.org spec.
    Returns detected schema types, validation errors, and recommended additions.

    Args:
        url: The page URL to audit (e.g. 'https://example.com/service-page')
    """
    return {
        "parse_html": run_script("parse_html.py", [url]),
        "validate_schema": run_script("validate_schema.py", [url]),
    }


@mcp.tool()
def seo_pagespeed(url: str, strategy: str = "mobile") -> dict:
    """
    Run a PageSpeed / Core Web Vitals audit via Google PageSpeed Insights API.
    Returns LCP, FID/INP, CLS scores plus performance opportunities and diagnostics.

    Args:
        url: The page URL to audit (e.g. 'https://example.com')
        strategy: Device strategy — 'mobile' (default) or 'desktop'
    """
    return run_script("pagespeed.py", [url, "--strategy", strategy])


@mcp.tool()
def seo_links(url: str, depth: int = 1, max_pages: int = 20) -> dict:
    """
    Audit the link profile, internal link structure, and broken links for a domain.
    Crawls up to max_pages pages at the given depth to surface orphaned pages,
    broken outbound links, and external link equity signals.

    Args:
        url: The domain to audit (e.g. 'https://example.com')
        depth: Crawl depth (default 1)
        max_pages: Maximum pages to crawl (default 20)
    """
    return {
        "link_profile": run_script("link_profile.py", [url, "--depth", str(depth), "--max-pages", str(max_pages)]),
        "internal_links": run_script("internal_links.py", [url, "--depth", str(depth), "--max-pages", str(max_pages)]),
        "broken_links": run_script("broken_links.py", [url, "--depth", str(depth), "--max-pages", str(max_pages)]),
    }


@mcp.tool()
def seo_sitemap(url: str) -> dict:
    """
    Audit the sitemap for broken or inaccessible URLs.
    Fetches and validates all URLs listed in the sitemap, flagging 4xx/5xx responses
    and redirects that indicate stale sitemap entries.

    Args:
        url: The domain whose sitemap to audit (e.g. 'https://example.com')
    """
    return run_script("broken_links.py", [url])


@mcp.tool()
def seo_geo_readiness(url: str) -> dict:
    """
    Assess a site's readiness for AI/LLM-era search (GEO — Generative Engine Optimisation).
    Checks for llms.txt presence, robots.txt AI directives, and HTML signals that
    affect how AI search engines and crawlers interpret the site.

    Args:
        url: The domain to audit (e.g. 'https://example.com')
    """
    return {
        "llms_txt": run_script("llms_txt_checker.py", [url]),
        "robots_checker": run_script("robots_checker.py", [url]),
        "parse_html": run_script("parse_html.py", [url]),
    }


@mcp.tool()
def seo_hreflang(url: str) -> dict:
    """
    Audit hreflang tags for international SEO correctness.
    Validates language/region codes, checks for missing return tags, and flags
    mismatches that could cause duplicate-content penalties across locales.

    Args:
        url: The domain or page URL to audit (e.g. 'https://example.com')
    """
    return run_script("hreflang_checker.py", [url])


@mcp.tool()
def seo_duplicate_content(url: str) -> dict:
    """
    Detect duplicate or near-duplicate content issues across a domain.
    Identifies pages with identical or heavily similar content, missing canonicals,
    and parameter-based duplication that dilutes crawl budget and ranking signals.

    Args:
        url: The domain to audit (e.g. 'https://example.com')
    """
    return run_script("duplicate_content.py", [url])


@mcp.tool()
def seo_competitor_gap(url: str, competitor: str) -> dict:
    """
    Run a keyword and content gap analysis between a target site and a competitor.
    Surfaces topics, keywords, and content formats the competitor ranks for
    that the target site is missing or underperforming on.

    Args:
        url: The target site URL (e.g. 'https://hedgehogmarketing.com.au')
        competitor: The competitor site URL (e.g. 'https://commacreative.com.au')
    """
    return run_script("competitor_gap.py", [url, "--competitor", competitor])


@mcp.tool()
def seo_indexnow(url: str, key: str) -> dict:
    """
    Submit a URL or domain to IndexNow for immediate indexing notification.
    Validates the IndexNow key file, then submits the URL to Bing and other
    IndexNow-compatible search engines for rapid re-crawl.

    Args:
        url: The URL to submit (e.g. 'https://example.com/new-page')
        key: The IndexNow API key for this domain
    """
    return run_script("indexnow_checker.py", [url, "--key", key])


@mcp.tool()
def seo_images(url: str) -> dict:
    """
    Audit image SEO signals on a page or domain.
    Checks alt text presence and quality, image dimensions, file size, and
    lazy-loading attributes that affect both accessibility and Core Web Vitals.

    Args:
        url: The page or domain URL to audit (e.g. 'https://example.com')
    """
    return run_script("parse_html.py", [url])


@mcp.tool()
def seo_full_audit(url: str) -> dict:
    """
    Run a comprehensive SEO audit across all core checks.
    Executes parse_html, pagespeed, robots_checker, security_headers, broken_links,
    and readability in sequence. Returns a combined findings dict keyed by check name.
    Expect this to take 60-90 seconds for a full domain.

    Args:
        url: The domain to audit (e.g. 'https://hedgehogmarketing.com.au')
    """
    return {
        "parse_html": run_script("parse_html.py", [url]),
        "pagespeed": run_script("pagespeed.py", [url]),
        "robots_checker": run_script("robots_checker.py", [url]),
        "security_headers": run_script("security_headers.py", [url]),
        "broken_links": run_script("broken_links.py", [url]),
        "readability": run_script("readability.py", [url]),
    }


@mcp.resource("health://status")
def health_check() -> str:
    """Health check endpoint — returns server status."""
    return json.dumps({"status": "ok", "server": "hedgehog-seo-auditor"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
