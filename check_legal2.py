"""Fetch legal pages content."""
from raspal import Fetcher, Extractor

f = Fetcher()
ext = Extractor()

for path, label in [("/terms-of-service", "Terms"), ("/legal-notice", "Legal Notice")]:
    r = f.fetch("https://es.talent.com" + path, cache_ttl=0)
    text = ext.extract_text(r.html) if r.html else ""
    print(f"=== {label} (status={r.status}) ===")
    print((text or "")[:1500])
    print()
