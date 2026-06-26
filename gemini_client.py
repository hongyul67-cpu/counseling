"""
Gemini API 클라이언트 (API 호출 전담)

프롬프트 조립 등 순수 로직은 core/logic.py 에 있습니다.
이 파일은 키 읽기와 실제 API 호출만 담당합니다.
"""

import streamlit as st
import google.generativeai as genai

from constants import GEMINI_MODEL
from core import logic


def _get_api_key() -> str | None:
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return None


def is_configured() -> bool:
    return bool(_get_api_key())


def generate_log(student_alias, counsel_date, topics, memo,
                 sections=None, previous_log=None):
    """
    일지 초안을 생성해 문자열로 반환.
    실패 시 (None, 오류메시지) 형태로 반환.
    """
    api_key = _get_api_key()
    if not api_key:
        return None, "API 키가 설정되지 않았습니다. 관리자에게 문의하세요."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)
        prompt = logic.build_prompt(
            student_alias, counsel_date, topics, memo,
            sections=sections, previous_log=previous_log,
        )
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        return None, f"일지 생성 중 오류가 발생했습니다: {e}"
