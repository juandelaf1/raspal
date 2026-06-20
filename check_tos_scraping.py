"""Check Talent.com ToS for scraping-related clauses."""
from raspal import Fetcher, Extractor

f = Fetcher()
ext = Extractor()

r = f.fetch("https://es.talent.com/terms-of-service", cache_ttl=0)
text = ext.extract_text(r.html) or ""
html = r.html or ""

# Search for scraping-related keywords
keywords = [
    "scrap", "robot", "bot", "crawl", "automat", "screen scrap",
    "data mining", "harvest", "extract", "collect", "prohib",
    "raspar", "automatico", "automatizado", "acceso automatizado",
    "sin permiso", "without permission", "prohibido",
]

for kw in keywords:
    idx = text.lower().find(kw.lower())
    if idx > -1:
        ctx = text[max(0, idx-200):idx+200]
        print(f"\n=== Found '{kw}' ===")
        print(ctx)
        print()

html_keywords = ["scrap", "crawl", "bot", "prohibit", "automat"]
for kw in html_keywords:
    idx = html.lower().find(kw)
    if idx > -1:
        ctx = html[max(0, idx-100):idx+300]
        cleaned = ctx.replace("\n", " ").replace("<", " <").replace(">", "> ")[:500]
        print(f"HTML '{kw}': ...{cleaned}...\n")
