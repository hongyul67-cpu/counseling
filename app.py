"""
상담 일지 자동 작성 도구 - 메인 진입점

실행:  streamlit run app.py
"""

import streamlit as st

from constants import PRIVACY_WARNING
from core import gemini_client
from ui import login, input_form, result_view, template_panel


st.set_page_config(page_title="상담 일지 작성 도구", page_icon="📝")


def _show_setup_guide():
    """관리자가 아직 키를 등록하지 않았을 때 보여주는 안내."""
    st.title("📝 상담 일지 작성 도구")
    st.error("아직 API 키가 설정되지 않았습니다. 관리자 설정이 필요합니다.")
    with st.expander("관리자 설정 방법 보기"):
        st.markdown(
            """
1. **Google AI Studio** (aistudio.google.com)에서 API 키를 발급받으세요.
2. 민감한 상담 내용을 다루므로 **결제가 연결된 유료 티어 키**를 권장합니다.
   (무료 티어는 입력 내용이 Google 모델 개선에 사용될 수 있습니다.)
3. 프로젝트의 `.streamlit/secrets.toml` 파일에 아래를 입력하세요:

    ```
    GEMINI_API_KEY = "발급받은-키"
    ACCESS_CODE = "상담사들에게-공유할-접근코드"
    ```
            """
        )


def main():
    # 1) 키 설정 여부 확인
    if not gemini_client.is_configured():
        _show_setup_guide()
        return

    # 2) 로그인
    if not login.require_login():
        return

    # '다음 학생' 요청이 있었으면, 위젯이 그려지기 전인 지금 초기화.
    if st.session_state.pop("_clear_requested", False):
        input_form.clear_inputs()

    # 3) 메인 화면
    st.title("📝 상담 일지 작성 도구")
    st.markdown(PRIVACY_WARNING)
    st.markdown("---")

    # 사이드바: 일지 양식 선택/편집 → 사용할 항목 리스트
    sections = template_panel.render_template_controls()

    inputs = input_form.render()

    # 4) 생성 처리
    if inputs["submitted"]:
        if not inputs["memo"]:
            st.warning("상담 메모를 입력해 주세요.")
            return
        if not inputs["student_alias"]:
            st.warning("학생 가명/이니셜을 입력해 주세요.")
            return

        with st.spinner("일지를 작성하는 중입니다..."):
            log_text, error = gemini_client.generate_log(
                inputs["student_alias"],
                inputs["counsel_date"],
                inputs["topics"],
                inputs["memo"],
                sections=sections,
                previous_log=inputs.get("previous_log") or None,
            )

        if error:
            st.error(error)
        else:
            st.session_state["last_log"] = log_text
            st.session_state["last_inputs"] = inputs

    # 5) 결과 표시 (생성 직후 또는 재실행 시 유지)
    if st.session_state.get("last_log"):
        result_view.render(
            st.session_state["last_log"],
            st.session_state["last_inputs"],
        )


if __name__ == "__main__":
    main()
