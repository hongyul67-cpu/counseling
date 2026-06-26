"""
양식 만들기 (별도 페이지)

상담 일지 양식을 차분히 설계해 JSON으로 저장하는 전용 도구입니다.
- 항목을 추가/삭제/위아래 이동
- 각 항목에 작성 가이드(선택) 입력
- 실시간 미리보기
- JSON 파일로 다운로드
- 기존 양식 JSON 을 불러와 수정 후 다시 저장

상담사는 JSON 문법을 전혀 몰라도 됩니다. 화면에서 만들면 JSON은 자동 생성됩니다.
"""

import streamlit as st

from constants import DEFAULT_LOG_SECTIONS
from core import template_loader

st.set_page_config(page_title="양식 만들기", page_icon="🗂")

st.title("🗂 일지 양식 만들기")
st.caption(
    "여기서 만든 양식을 JSON 파일로 저장한 뒤, 메인 화면의 '양식 불러오기'에 올리면 "
    "그 구성대로 일지가 작성됩니다. JSON 문법은 몰라도 됩니다."
)

# ──────────────────────────────────────────────────────────────
# 작업 중인 양식을 세션에 보관 (항목: {title, guide} 리스트)
# ──────────────────────────────────────────────────────────────
if "builder_sections" not in st.session_state:
    st.session_state["builder_sections"] = [
        {"title": s, "guide": ""} for s in DEFAULT_LOG_SECTIONS
    ]
if "builder_name" not in st.session_state:
    st.session_state["builder_name"] = "우리기관 상담일지"


def _move(idx, delta):
    secs = st.session_state["builder_sections"]
    new = idx + delta
    if 0 <= new < len(secs):
        secs[idx], secs[new] = secs[new], secs[idx]


def _delete(idx):
    st.session_state["builder_sections"].pop(idx)


# ──────────────────────────────────────────────────────────────
# 기존 양식 불러와 수정하기
# ──────────────────────────────────────────────────────────────
with st.expander("기존 양식 불러와 수정하기"):
    up = st.file_uploader("양식 .json 파일", type=["json"], key="builder_upload")
    if up is not None:
        try:
            tpl = template_loader.load_template(up.read())
            st.session_state["builder_sections"] = tpl["sections"]
            st.session_state["builder_name"] = tpl["name"]
            st.success(f"'{tpl['name']}' 양식을 불러왔습니다. 아래에서 수정하세요.")
        except template_loader.TemplateError as e:
            st.error(str(e))

st.markdown("---")

# ──────────────────────────────────────────────────────────────
# 양식 이름
# ──────────────────────────────────────────────────────────────
st.session_state["builder_name"] = st.text_input(
    "양식 이름",
    value=st.session_state["builder_name"],
)

# ──────────────────────────────────────────────────────────────
# 항목 편집
# ──────────────────────────────────────────────────────────────
st.markdown("#### 일지 항목")
st.caption("각 항목의 제목과, 필요하면 작성 가이드를 적으세요. 가이드는 AI가 참고합니다.")

sections = st.session_state["builder_sections"]

for idx, sec in enumerate(sections):
    with st.container(border=True):
        sec["title"] = st.text_input(
            f"{idx + 1}. 항목 제목",
            value=sec.get("title", ""),
            key=f"title_{idx}",
        )
        sec["guide"] = st.text_input(
            "작성 가이드 (선택)",
            value=sec.get("guide", ""),
            placeholder="예: 다음 회기 목표와 일정을 포함",
            key=f"guide_{idx}",
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            st.button("▲ 위로", key=f"up_{idx}", use_container_width=True,
                      on_click=_move, args=(idx, -1), disabled=(idx == 0))
        with c2:
            st.button("▼ 아래로", key=f"down_{idx}", use_container_width=True,
                      on_click=_move, args=(idx, 1),
                      disabled=(idx == len(sections) - 1))
        with c3:
            st.button("🗑 삭제", key=f"del_{idx}", use_container_width=True,
                      on_click=_delete, args=(idx,),
                      disabled=(len(sections) <= 1))

if st.button("➕ 항목 추가", use_container_width=True):
    sections.append({"title": "", "guide": ""})
    st.rerun()

st.markdown("---")

# ──────────────────────────────────────────────────────────────
# 미리보기 + 저장
# ──────────────────────────────────────────────────────────────
valid_sections = [s for s in sections if s.get("title", "").strip()]

st.markdown("#### 미리보기")
if valid_sections:
    preview = template_loader.sections_for_prompt(valid_sections)
    st.code(preview, language=None)
else:
    st.info("제목이 있는 항목을 하나 이상 추가하면 미리보기가 표시됩니다.")

name = st.session_state["builder_name"]
if valid_sections:
    st.download_button(
        "💾 이 양식을 JSON 파일로 저장",
        data=template_loader.export_template(name, valid_sections),
        file_name=f"{(name or '양식').strip()}.json",
        mime="application/json",
        type="primary",
        use_container_width=True,
    )
    st.caption("저장한 파일을 메인 화면의 '양식 불러오기'에 올려서 사용하세요.")
else:
    st.warning("저장하려면 제목이 있는 항목이 최소 하나 필요합니다.")
