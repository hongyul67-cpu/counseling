"""
상담 정보 입력 폼

모바일에서도 편하게 위→아래로 읽히도록 세로 배치를 기본으로 합니다.
학생 가명에 실명으로 의심되는 패턴이 들어오면 부드럽게 한 번 더 경고합니다.

모든 입력 위젯에 key 를 부여합니다. '다음 학생' 초기화(clear_inputs)가
이 key 들을 비워 깨끗한 상태로 되돌릴 수 있게 하기 위함입니다.
"""

import streamlit as st
import datetime
import re

from constants import COUNSELING_TOPICS

# 이 폼이 사용하는 위젯 key 목록 (초기화 시 사용)
INPUT_WIDGET_KEYS = [
    "in_alias", "in_date", "in_session", "in_topics", "in_memo",
    "prev_log_uploader",
]


def _looks_like_real_name(text: str) -> bool:
    """한글 2~4자만으로 이루어진 입력은 실명일 가능성이 있어 경고용으로 감지."""
    cleaned = text.strip()
    return bool(re.fullmatch(r"[가-힣]{2,4}", cleaned))


def clear_inputs():
    """입력 위젯과 직전 결과를 모두 비워 '다음 학생' 상태로 초기화."""
    for k in INPUT_WIDGET_KEYS:
        st.session_state.pop(k, None)
    st.session_state.pop("last_log", None)
    st.session_state.pop("last_inputs", None)


def render():
    """입력값을 dict 로 반환. 아직 생성 버튼을 누르지 않았으면 submitted=False."""
    st.markdown("#### 📝 상담 정보 입력")

    student_alias = st.text_input(
        "학생 (가명/이니셜)",
        placeholder="예: A군, 김OO, 이니셜 J.H.",
        key="in_alias",
    )
    if student_alias and _looks_like_real_name(student_alias):
        st.warning("실명일 수 있습니다. 가명이면 이 안내는 무시하셔도 됩니다.")

    counsel_date = st.date_input(
        "상담 날짜", value=datetime.date.today(), key="in_date"
    )

    session_no = st.number_input(
        "상담 회차 (선택 — 모르면 비워두세요)",
        min_value=0,
        step=1,
        value=0,
        key="in_session",
        help="같은 학생의 몇 번째 상담인지 직접 입력합니다. 0이면 파일명에 표시되지 않습니다.",
    )

    topics = st.multiselect(
        "상담 유형 (복수 선택 가능)",
        options=COUNSELING_TOPICS,
        key="in_topics",
    )

    memo = st.text_area(
        "상담 메모 (키워드·요점)",
        height=180,
        placeholder="상담 중 메모한 키워드나 요점을 자유롭게 적어 주세요.\n예: 최근 시험 성적 하락, 부모와 갈등, 수면 부족 호소...",
        key="in_memo",
    )

    # 이전 회차 일지 업로드 (선택) — 연속성 참고용
    previous_log = ""
    with st.expander("📎 이전 회차 일지 첨부 (선택) — 상담 흐름 이어가기"):
        st.caption(
            "지난 회차에 저장해 둔 .txt 일지를 올리면, 이번 일지가 그 맥락을 참고해 작성됩니다. "
            "파일은 이번 작성에만 쓰이며 어디에도 저장되지 않습니다."
        )
        prev_file = st.file_uploader(
            "이전 회차 .txt 파일",
            type=["txt"],
            key="prev_log_uploader",
        )
        if prev_file is not None:
            try:
                previous_log = prev_file.read().decode("utf-8").strip()
                st.success("이전 회차 내용을 참고합니다.")
            except Exception:
                st.warning("파일을 읽지 못했습니다. UTF-8 텍스트 파일인지 확인해 주세요.")

    submitted = st.button("일지 작성하기", type="primary", use_container_width=True)

    return {
        "student_alias": student_alias.strip(),
        "counsel_date": counsel_date.strftime("%Y-%m-%d"),
        "session_no": int(session_no),
        "topics": topics,
        "memo": memo.strip(),
        "previous_log": previous_log,
        "submitted": submitted,
    }
