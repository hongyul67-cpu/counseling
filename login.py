"""
간단한 접근 통제

- 본격적인 인증 시스템이 아니라, '아무나 못 들어오게' 하는 최소 장치입니다.
- 접근 코드는 st.secrets 의 ACCESS_CODE 와 비교합니다.
- 통과하면 상담사 이름을 세션에 기록합니다(일지 작성자 표기에 활용 가능).
"""

import streamlit as st


def _correct_code() -> str | None:
    try:
        return st.secrets["ACCESS_CODE"]
    except (KeyError, FileNotFoundError):
        return None


def require_login() -> bool:
    """
    로그인 상태면 True. 아니면 로그인 폼을 그리고 False 반환.
    호출하는 쪽에서 False면 이후 화면을 그리지 않도록 합니다.
    """
    if st.session_state.get("authenticated"):
        return True

    st.subheader("🔐 접근 확인")
    st.caption("기관 내 상담사 전용 도구입니다.")

    name = st.text_input("상담사 이름", placeholder="예: 홍길동", key="login_name")
    code = st.text_input("접근 코드", type="password", key="login_code")

    if st.button("입장", key="login_submit"):
        expected = _correct_code()
        if expected is None:
            st.error("접근 코드가 설정되지 않았습니다. 관리자에게 문의하세요.")
        elif not name.strip():
            st.warning("이름을 입력해 주세요.")
        elif code == expected:
            st.session_state["authenticated"] = True
            st.session_state["counselor_name"] = name.strip()
            st.rerun()
        else:
            st.error("접근 코드가 올바르지 않습니다.")

    return False
