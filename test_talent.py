from raspal import Fetcher, Extractor
f = Fetcher()
r = f.fetch("https://es.talent.com/salary?job=data+scientist", cache_ttl=0)
ext = Extractor()

print("=== TEXT (first 1000 chars) ===")
print(f"html length: {len(r.html) if r.html else 0}")
print(f"text: {r.text[:500] if r.text else 'None'}")
print(f"status: {r.status}")
print(f"attrs: {dir(r)}")

print("\n=== SELECTORS ===")
data = ext.extract_selectors(r.html, {
    "salary": ".salary-amount, [class*=salary], .text-2xl, .average-salary, .salary__amount, strong",
    "table": "table",
    "list": "ul",
})
for k, v in data.items():
    if v:
        print(f"{k}: {str(v)[:300]}")
    else:
        print(f"{k}: None")
