"""직무 분류 (규칙 기반, LLM 사용 금지 — F-02 조건).

분류 신호는 두 가지이며 우선순위가 있다.
  1순위: ATS가 제공하는 구조화 필드(occupation / job) — 채용 담당자가 직접 고른 값
  2순위: 공고 제목 키워드 — 구조화 필드가 없거나 매칭 실패할 때의 fallback

두 신호가 서로 다른 결과를 내면 1순위를 채택하되 불일치 사실을 기록한다.
"""

import re

CATEGORIES = ["서버·백엔드", "웹 프론트엔드", "모바일", "데이터·AI"]

# 공고 제목용 키워드 (기능명세 스펙 원본)
JOB_KEYWORDS = {
    "서버·백엔드": ["백엔드", "서버", "Backend", "Server"],
    "웹 프론트엔드": ["프론트엔드", "웹", "Frontend", "Web"],
    "모바일": ["모바일", "iOS", "Android", "안드로이드"],
    "데이터·AI": ["데이터", "AI", "머신러닝", "ML", "인공지능", "Data"],
}

# 구조화 필드(occupation / job)용 키워드.
# ATS 직무 분류 체계는 "Back-end Engineering", "Data Scientist"처럼
# 제목과 표기가 달라서 별도 사전이 필요하다.
STRUCTURED_KEYWORDS = {
    "서버·백엔드": [
        "백엔드", "서버", "Backend", "Back-end", "Back End", "Server",
        "API", "DevOps", "SRE", "인프라", "Infrastructure", "Platform Engineering",
    ],
    "웹 프론트엔드": [
        "프론트엔드", "프론트", "웹", "Frontend", "Front-end", "Front End", "Web",
    ],
    "모바일": [
        "모바일", "Mobile", "iOS", "Android", "안드로이드", "Flutter", "React Native",
    ],
    "데이터·AI": [
        "데이터", "Data", "AI", "머신러닝", "ML", "인공지능", "MLOps",
        "Machine Learning", "Analytics", "분석", "Scientist",
    ],
}

# 짧은 ASCII 토큰은 부분일치 오탐이 크다.
# 예: "AI"가 "retail"에, "ML"이 "HTML"에, "Web"이 "Webtoon"에 걸린다.
# 그래서 ASCII 키워드는 단어 경계(\b) 기준으로만 매칭한다.
_ASCII_ONLY = re.compile(r"^[A-Za-z][A-Za-z\s\-]*$")


def _matches(keyword, text):
    if _ASCII_ONLY.match(keyword):
        return re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE) is not None
    return keyword in text


def _classify_with(keyword_map, text):
    if not text:
        return None
    for category, keywords in keyword_map.items():
        if any(_matches(kw, text) for kw in keywords):
            return category
    return None


def classify_from_structured(occupation=None, job=None):
    """ATS 구조화 필드로 분류. job(세부 직무)이 occupation(직군)보다 구체적이므로 먼저 본다."""
    return _classify_with(STRUCTURED_KEYWORDS, job) or _classify_with(STRUCTURED_KEYWORDS, occupation)


def classify_from_title(title):
    """공고 제목 키워드로 분류."""
    return _classify_with(JOB_KEYWORDS, title)


def classify_job(title, occupation=None, job=None):
    """직무 분류 결과를 dict로 반환.

    반환 키:
      category        최종 분류 (없으면 None → 집계에서 제외)
      source          "structured" | "title" | None
      structured      구조화 필드 기반 분류 결과
      title_based     제목 기반 분류 결과
      disagreement    두 신호가 모두 있고 결과가 다르면 True
    """
    structured = classify_from_structured(occupation, job)
    title_based = classify_from_title(title)

    if structured:
        category, source = structured, "structured"
    elif title_based:
        category, source = title_based, "title"
    else:
        category, source = None, None

    return {
        "category": category,
        "source": source,
        "structured": structured,
        "title_based": title_based,
        "disagreement": bool(structured and title_based and structured != title_based),
    }
