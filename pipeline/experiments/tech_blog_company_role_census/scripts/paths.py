from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
EXPERIMENT = PROJECT_ROOT / "pipeline" / "experiments" / "tech_blog_company_role_census"
WORK = PROJECT_ROOT / "data" / "work" / "tech_blog_company_role_census"
RESEARCH = PROJECT_ROOT / "data" / "research" / "tech_blog_company_role_census"
COMPANIES_FILE = EXPERIMENT / "config" / "companies.json"
COLLECTED_DIR = WORK / "collected"
ARTICLES_FILE = COLLECTED_DIR / "articles.json"
COLLECT_REPORT = COLLECTED_DIR / "collect_report.json"
ROUND2_REPORT = COLLECTED_DIR / "round2_report.json"
PRIORITY_REPORT = COLLECTED_DIR / "priority_report.json"
EXPAND_REPORT = COLLECTED_DIR / "expand_report.json"
TITLE_BACKFILL_REPORT = COLLECTED_DIR / "title_backfill_report.json"
EXTRACTED_FILE = WORK / "extracted" / "articles.json"
EXTRACT_REPORT = WORK / "extracted" / "extract_report.json"
CLASSIFIED_FILE = WORK / "classified" / "articles.json"
