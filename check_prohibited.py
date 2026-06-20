"""Extract prohibited activities section from Talent.com ToS."""
from raspal import Fetcher, Extractor

f = Fetcher()
ext = Extractor()

r = f.fetch("https://es.talent.com/terms-of-service", cache_ttl=0)
text = ext.extract_text(r.html) or ""

# Find prohibited activities section
idx = text.lower().find("actividades prohibidas")
if idx == -1:
    idx = text.lower().find("prohibited")
if idx == -1:
    idx = text.lower().find("prohibido")

if idx > -1:
    # Print from prohibited section onwards
    section = text[idx:idx+2000]
    print("=== ACTIVIDADES PROHIBIDAS ===")
    print(section)
else:
    print("No 'prohibited activities' section found")
    # Print last part of ToS where it usually is
    print("\n=== LAST 2000 CHARS ===")
    print(text[-2000:])
