# Legal and Ethical Use of RASPAL SCRAPER

RASPAL SCRAPER is a technical tool. How you use it determines whether your activities are legal and ethical.

## Core Principles

1. **Respect robots.txt** — Check `https://example.com/robots.txt` before scraping
2. **Read Terms of Service** — Some sites explicitly prohibit automated access
3. **Rate limit your requests** — Use AutoThrottle to avoid overwhelming servers
4. **Don't scrape personal data** — GDPR, CCPA, and other privacy laws apply
5. **Don't bypass anti-bot measures** — Using stealth mode doesn't make it legal
6. **Use public data only** — Don't access data behind authentication or paywalls

## Compliance Checklist

Before scraping any website, ask yourself:

- [ ] Did I check the robots.txt file?
- [ ] Did I read the Terms of Service?
- [ ] Am I respecting rate limits?
- [ ] Am I scraping only public data?
- [ ] Am I not collecting personal information?
- [ ] Am I not bypassing authentication or paywalls?
- [ ] Am I not causing harm to the target website?

## Legal Disclaimer

RASPAL SCRAPER is provided as-is. The developers are not responsible for how users employ this tool. You are solely responsible for ensuring your scraping activities comply with all applicable laws, regulations, and website policies.

If you're unsure whether your use case is legal, consult a legal professional.

## Ethical Scraping Guidelines

- **Be transparent** — Identify yourself in User-Agent headers
- **Be respectful** — Don't overload servers with requests
- **Be selective** — Only collect what you actually need
- **Be accountable** — Keep logs of what you scrape and why

## Compliance Helper

Use the built-in compliance checker before running a scrape:

```python
from raspal import check_compliance

result = check_compliance("https://example.com")
print(result["warnings"])
```

This provides basic signals (robots.txt URL, sensitive domain detection) but does not make legal determinations.
