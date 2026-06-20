"""Scrape Talent.com Spain for all DataScope roles using RASPAL."""
import re
import json
import time
from pathlib import Path
from raspal import Fetcher, RequestQueue, Pipeline, Extractor

ROLES = [
    "data+scientist",
    "data+engineer",
    "data+analyst",
    "machine+learning",
    "ai+engineer",
    "business+intelligence",
    "data+architect",
    "analytics+engineer",
    "backend+engineer",
    "frontend+engineer",
    "fullstack+engineer",
    "devops+engineer",
    "mobile+engineer",
    "qa+engineer",
    "sysadmin",
    "security+engineer",
    "cloud+engineer",
    "data+manager",
    "research+scientist",
    "computer+vision",
    "nlp+engineer",
    "data+manager/senior",
    "head+of+data",
]

BASE_URL = "https://es.talent.com/salary?job={role}"

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def extract_salaries(html: str, metadata: dict) -> dict:
    result = {
        "role": None,
        "avg_salary_eur": None,
        "avg_salary_period": None,
        "entry_salary_eur": None,
        "senior_salary_eur": None,
        "hourly_rate_eur": None,
    }

    # Role from meta title
    title = metadata.get("title", "")
    m = re.search(r'^(.+?)\s+Salario', title)
    if m:
        result["role"] = m.group(1).strip()
    elif title:
        result["role"] = title.split("Salario")[0].strip()

    # Meta description
    desc = metadata.get("description", "")
    if desc:
        m = re.search(r'media de\s*[€$]\s*([\d.,]+)\s*/\s*(\w+)', desc)
        if m:
            result["avg_salary_eur"] = float(m.group(1).replace(".", "").replace(",", "."))
            result["avg_salary_period"] = m.group(2)
        m = re.search(r'[€$]\s*([\d.,]+)\s*/\s*hora', desc)
        if m:
            result["hourly_rate_eur"] = float(m.group(1).replace(",", "."))

    # Parse HTML directly for entry/senior breakdown
    # "Los puestos de nivel inicial empiezan en € 20.800 al año"
    m = re.search(r'nivel inicial empiezan en\s*[€$]\s*([\d.,]+)', html)
    if m:
        result["entry_salary_eur"] = float(m.group(1).replace(".", "").replace(",", "."))

    # "los trabajadores más experimentados ganan hasta € 46.941 al año"
    m = re.search(r'más experimentados ganan hasta\s*[€$]\s*([\d.,]+)', html)
    if m:
        result["senior_salary_eur"] = float(m.group(1).replace(".", "").replace(",", "."))

    return result


RESULT_CACHE = {}


def scrape_role(fetcher, ext, role_slug):
    url = BASE_URL.format(role=role_slug)
    print(f"  Fetching: {url}")

    result = fetcher.fetch(url, engine="scrapling", cache_ttl=86400)
    if result.status != 200 or not result.html:
        print(f"    ERROR: status={result.status}")
        return None

    metadata = ext.extract_metadata(result.html)
    data = extract_salaries(result.html, metadata)
    data["url"] = url

    role_name = role_slug.replace("+", " ").title()
    print(f"    Role: {data.get('role') or role_name}")
    avg = data.get('avg_salary_eur')
    ent = data.get('entry_salary_eur')
    sen = data.get('senior_salary_eur')
    print(f"    Avg: {avg}/yr" if avg else "    Avg: N/A")
    print(f"    Entry: {ent}" if ent else "    Entry: N/A")
    print(f"    Senior: {sen}" if sen else "    Senior: N/A")

    return data


def scrape_all():
    fetcher = Fetcher()
    ext = Extractor()
    pipeline = Pipeline()

    for i, role_slug in enumerate(ROLES):
        print(f"[{i+1}/{len(ROLES)}] {role_slug.replace('+',' ').title()}")
        try:
            data = scrape_role(fetcher, ext, role_slug)
            if data:
                pipeline.add(url=data["url"], data=data)
            time.sleep(1.5)
        except Exception as e:
            print(f"    ERROR: {e}")
            continue

    # Save
    out_json = DATA_DIR / "talent_spain_salaries.json"
    pipeline.to_json(str(out_json))
    print(f"\nDone! {len(pipeline)} roles scraped -> {out_json}")

    out_csv = DATA_DIR / "talent_spain_salaries.csv"
    pipeline.to_csv(str(out_csv))
    print(f"CSV -> {out_csv}")

    return pipeline


if __name__ == "__main__":
    scrape_all()
