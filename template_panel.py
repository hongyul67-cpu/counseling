"""
일지 양식 선택 (사이드바)

역할을 단순화했습니다:
- 양식을 새로 만들거나 수정하는 일은 '양식 만들기' 전용 페이지가 담당합니다.
- 사이드바에서는 저장된 양식 JSON을 '불러와서 적용'하기만 합니다.

선택된 양식의 항목 리스트({title, guide} dict)는 반환되어 일지 생성에 사용됩니다.
양식을 올리지 않으면 기본 항목이 쓰입니다.
"""

import streamlit as st

from constants import DEFAULT_LOG_SECTIONS
from core import template_loader


def render_template_controls():
    """현재 사용할 일지 항목 리스트를 반환."""
    st.sidebar.markdown("### 🗂 일지 양식")

    # 세션에 현재 양식 보관 (없으면 기본값을 {title, guide} 구조로)
    if "sections" not in st.session_state:
        st.session_state["sections"] = [
            {"title": s, "guide": ""} for s in DEFAULT_LOG_SECTIONS
        ]
        st.session_state["template_name"] = "기본 양식"

    # 저장된 양식 불러오기
    up = st.sidebar.file_uploader(
        "양식 JSON 불러오기", type=["json"], key="tpl_uploader"
    )
    if up is not None:
        try:
            tpl = template_loader.load_template(up.read())
            st.session_state["sections"] = tpl["sections"]
            st.session_state["template_name"] = tpl["name"]
            st.sidebar.success(f"'{tpl['name']}' 양식 적용됨")
        except template_loader.TemplateError as e:
            st.sidebar.error(str(e))

    st.sidebar.caption(
        f"현재 양식: **{st.session_state.get('template_name', '기본 양식')}**"
    )
    st.sidebar.caption("양식을 새로 만들려면 왼쪽 메뉴의 '양식 만들기'로 이동하세요.")

    return st.session_state["sections"]
