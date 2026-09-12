"""실험 코드와 저장소 데이터 경로.

수집 원문과 임시 결과는 Git에서 제외되는 data/work에 두고,
공유 가능한 집계만 data/research에 둡니다.
"""

from pathlib import Path

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]

WORK_DIR = REPO_ROOT / "data" / "work" / "job_postings"
RAW_DIR = WORK_DIR / "raw"
PROCESSED_DIR = WORK_DIR / "processed"
LOG_DIR = WORK_DIR / "logs"
PROBE_DIR = WORK_DIR / "probe"

RESEARCH_DIR = REPO_ROOT / "data" / "research" / "job_postings"
