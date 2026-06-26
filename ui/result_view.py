"""
일지 결과 출력

- AI 초안임을 명시하고, 상담사가 직접 수정할 수 있게 편집 가능한 영역으로 보여줍니다.
- 위기 관련 주제가 선택되거나 메모에 위기 신호가 있으면 안전 안내를 띄웁니다.
- 파일명은 안전하게 처리되며, .txt 는 메모리에서 바로 다운로드(서버 미저장)됩니다.
"""

import datetime
import streamlit as st

from constants import AI_DISCLAIMER, CRISIS_NOTICE, CRISIS_RELATED_TOPICS
from core import logic


def render(log_text, inputs):
    """생성된 일지(log_text)와 입력값(inputs)을 받아 결과 화면을 그립니다."""
    st.markdown("---")
    st.markdown("#### 📄 작성된 상담 일지")

    # 위기 안내: 주제 + 메모 내용 양쪽을 봄
    if logic.detect_crisis(inputs["topics"], inputs.get("memo", ""),
                           CRISIS_RELATED_TOPICS):
        st.error(CRISIS_NOTICE)

    st.info(AI_DISCLAIMER)

    edited = st.text_area(
        "내용을 검토하고 필요하면 수정하세요.",
        value=log_text,
        height=420,
    )

    session_no = inputs.get("session_no", 0)
    filename = logic.build_filename(
        inputs["student_alias"], inputs["counsel_date"], session_no
    )

    counselor = st.session_state.get("counselor_name", "")
    header = f"상담사: {counselor}\n" if counselor else ""
    session_line = f"상담회차: {session_no}회차\n" if session_no else ""
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    download_body = (
        f"{header}"
        f"대상: {inputs['student_alias']}\n"
        f"상담일자: {inputs['counsel_date']}\n"
        f"{session_line}"
        f"상담유형: {', '.join(inputs['topics']) if inputs['topics'] else '미지정'}\n"
        f"작성시각: {created_at}\n"
        f"{'-' * 30}\n"
        f"{edited}\n"
    )

    st.download_button(
        "📥 .txt 파일로 저장",
        data=download_body.encode("utf-8"),
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
    )

    # 연속 상담 동선: 저장 후 입력·결과를 비우고 다음 학생으로.
    # 위젯 생성 후 같은 실행에서 key 를 지우면 Streamlit 이 에러를 낼 수 있어,
    # 플래그만 세우고 실제 초기화는 다음 실행 시작 때 app.py 가 수행합니다.
    st.markdown("")
    if st.button("🧹 저장했어요 — 다음 학생 (입력 비우기)",
                 use_container_width=True):
        st.session_state["_clear_requested"] = True
        st.rerun()
    st.caption(
        "다음 학생으로 넘어가기 전에 위 버튼을 누르면 입력과 결과가 모두 지워져, "
        "이전 학생 정보가 화면에 남지 않습니다."
    )
