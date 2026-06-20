"""Transform Talent.com scraped data into DataScope unified format."""
import json
import csv
from pathlib import Path

ROLE_MAP = {
    "data scientist": "Data Scientist",
    "data engineer": "Data Engineer",
    "data analyst": "Data Analyst",
    "machine learning": "Machine Learning Engineer",
    "ai engineer": "AI Engineer",
    "business intelligence": "Business Intelligence",
    "data architect": "Data Architect",
    "analytics engineer": "Analytics Engineer",
    "backend engineer": "Backend Engineer",
    "frontend engineer": "Frontend Engineer",
    "fullstack engineer": "Fullstack Engineer",
    "devops engineer": "DevOps Engineer",
    "mobile engineer": "Mobile Engineer",
    "qa engineer": "QA Engineer",
    "sysadmin": "SysAdmin",
    "security engineer": "Security Engineer",
    "cloud engineer": "Cloud Engineer",
    "data manager": "Data Manager",
    "research scientist": "Research Scientist",
    "computer vision": "Computer Vision Engineer",
    "nlp engineer": "NLP Engineer",
}

OUTPUT_COLUMNS = [
    "source", "source_type", "country", "country_name", "region",
    "year", "job_title", "role_category", "experience_level",
    "employment_type", "salary_local", "currency", "salary_usd",
    "remote_ratio", "company_size", "company_location",
    "latitude", "longitude",
]


def transform(input_path: str, output_path: str):
    with open(input_path, encoding="utf-8") as f:
        raw = json.load(f)

    rows = []

    for item in raw:
        data = item.get("data", {})
        role_slug = data.get("role", "")
        role_category = ROLE_MAP.get(role_slug.lower().strip(), role_slug)

        # Create one record per experience level from Talent.com
        base = {
            "source": "Talent.com",
            "source_type": "scraper",
            "country": "ES",
            "country_name": "Spain",
            "region": "Europe",
            "year": 2026,
            "job_title": role_slug,
            "role_category": role_category,
            "employment_type": "Full-time",
            "currency": "EUR",
            "remote_ratio": 0,
            "company_size": "M",
            "company_location": "Spain",
            "latitude": 40.4168,
            "longitude": -3.7038,
        }

        # Average salary (all levels)
        if data.get("avg_salary_eur"):
            row = {**base,
                   "experience_level": "All",
                   "salary_local": data["avg_salary_eur"],
                   "salary_usd": round(data["avg_salary_eur"] * 1.08, 2)}
            rows.append(row)

        # Entry level
        if data.get("entry_salary_eur"):
            row = {**base,
                   "experience_level": "Entry",
                   "salary_local": data["entry_salary_eur"],
                   "salary_usd": round(data["entry_salary_eur"] * 1.08, 2)}
            rows.append(row)

        # Senior level
        if data.get("senior_salary_eur"):
            row = {**base,
                   "experience_level": "Senior",
                   "salary_local": data["senior_salary_eur"],
                   "salary_usd": round(data["senior_salary_eur"] * 1.08, 2)}
            rows.append(row)

    # Write CSV
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Transformed {len(rows)} records -> {output_path}")
    return rows


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent / "data"
    transform(
        str(data_dir / "talent_spain_salaries.json"),
        str(data_dir / "talent_spain_unified.csv"),
    )
