"""Check Talent.com legal pages."""
from raspal import Fetcher
f = Fetcher()
paths = ["/terms", "/terms-of-service", "/legal", "/legal-notice", "/privacy"]
for path in paths:
    r = f.fetch("https://es.talent.com" + path, cache_ttl=0)
    title = ""
    if r.metadata:
        title = str(r.metadata.get("title", ""))[:80]
    print(f"{path}: status={r.status}, title={title}")
