"""
순수 로직 모음 (streamlit 비의존)

이 파일은 streamlit 을 import 하지 않습니다.
덕분에 프롬프트 조립·파일명 생성·위기 감지 같은 핵심 로직을
단독으로 테스트할 수 있습니다.
"""

import re
import datetime

from constants import DEFAULT_LOG_SECTIONS, CRISIS_KEYWORDS
from core import template_loader


# ──────────────────────────────────────────────────────────────
# 파일명 안전 처리
# ──────────────────────────────────────────────────────────────
def sanitize_for_filename(text: str) -> str:
    """
    파일명에 쓸 수 없는 문자를 안전하게 치환.
    윈도/맥/리눅스에서 문제되는 문자: / \\ : * ? " < > | 및 제어문자.
    """
    if not text:
        return ""
    # 금지 문자를 밑줄로
    cleaned = re.sub(r'[\\/:*?"<>|]', "_", text)
    # 제어문자 제거
    cleaned = re.sub(r"[\x00-\x1f]", "", cleaned)
    # 앞뒤 공백/마침표 정리 (윈도는 끝 마침표/공백을 싫어함)
    cleaned = cleaned.strip().strip(".").strip()
    # 너무 길면 자르기
    return cleaned[:50]


def build_filename(student_alias: str, counsel_date: str,
                   session_no: int, now: datetime.datetime | None = None) -> str:
    """이니셜_날짜_회차_시각.txt 형식의 안전한 파일명 생성."""
    now = now or datetime.datetime.now()
    alias = sanitize_for_filename(student_alias) or "상담"
    time_str = now.strftime("%H%M%S")
    session_part = f"_{session_no}회차" if session_no else ""
    return f"{alias}_{counsel_date}{session_part}_{time_str}.txt"


# ──────────────────────────────────────────────────────────────
# 위기 감지 (주제 + 메모 내용 양쪽)
# ──────────────────────────────────────────────────────────────
def detect_crisis(topics, memo, crisis_topics) -> bool:
    """
    위기 안내를 띄울지 판단.
    - 선택된 주제가 위기 관련 주제에 포함되거나
    - 메모에 위기 신호 키워드가 있으면 True.
    """
    if any(t in crisis_topics for t in (topics or [])):
        return True
    text = (memo or "")
    return any(kw in text for kw in CRISIS_KEYWORDS)


# ──────────────────────────────────────────────────────────────
# 프롬프트 조립
# ──────────────────────────────────────────────────────────────
def build_prompt(student_alias, counsel_date, topics, memo,
                 sections=None, previous_log=None) -> str:
    """상담 정보를 바탕으로 일지 작성 프롬프트를 조립."""
    topic_str = ", ".join(topics) if topics else "미지정"
    sections = sections or DEFAULT_LOG_SECTIONS
    section_str = template_loader.sections_for_prompt(sections)

    prev_block = ""
    if previous_log:
        prev_block = f"""
[이전 회차 일지 — 맥락 참고용]
아래는 같은 학생의 지난 상담 기록입니다. 이번 회기의 흐름과 연속성을 이해하는 데만
참고하고, 이전 내용을 이번 일지에 그대로 옮겨 적지 마세요.
\"\"\"
{previous_log}
\"\"\"
"""

    return f"""당신은 청소년 상담 분야의 숙련된 전문상담사입니다.
아래 상담 메모를 바탕으로 표준화된 상담 일지를 작성하세요.

[가장 중요한 원칙 — 반드시 지킬 것]
- 상담 일지는 사실 기록입니다. 메모에 명시되지 않은 내용을 절대 지어내지 마세요.
- 메모에 없는 관찰·감정·진단·임상적 표현을 추가하지 마세요.
  (예: 메모에 없는데 '자살 사고를 호소하였다', '심각한 우울을 보였다' 등으로 단정 금지)
- 정보가 부족한 항목은 비워두지 말고 정확히 "추가 확인 필요"라고 적으세요.
- 추측이 필요한 경우, 단정하지 말고 "~로 보임", "~을 언급함" 처럼 관찰 수준으로만 기술하세요.
- 의심스러우면 더 적게, 더 신중하게 쓰세요. 과장보다 누락이 안전합니다.

[문체]
- 공적이고 간결하며 객관적인 전문 상담 문체.
- 대상·일자·상담유형 등 기본 정보는 일지 파일 머리말에 따로 기록되므로,
  본문에서는 다시 적지 말고 상담 내용 자체에만 집중하세요.

[일지 항목 — 이 구조를 따르세요]
{section_str}
{prev_block}
[상담 정보]
- 대상(가명/이니셜): {student_alias}
- 상담 일자: {counsel_date}
- 상담 유형: {topic_str}

[이번 회기 상담 메모]
{memo}
"""
