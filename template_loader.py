"""
상담 일지 양식 (template) 처리

설계 의도:
- 양식은 JSON으로 저장합니다 (프로그램이 이해하기 쉬움).
- 그러나 상담사가 JSON을 손으로 작성할 필요는 없습니다.
  양식 제작 페이지에서 항목을 편집한 뒤 export_template()로 JSON을 내려받고,
  다음에 그 파일을 load_template()로 올리면 같은 양식이 복원됩니다.

양식 JSON 구조:
{
    "name": "우리기관 표준 상담일지",
    "sections": [
        {"title": "기본 정보", "guide": "대상·일자·상담 유형을 적습니다"},
        {"title": "호소 문제", "guide": ""},
        ...
    ]
}

하위 호환:
- 예전 형식처럼 sections 가 단순 문자열 리스트여도 읽을 수 있습니다.
  ["기본 정보", "호소 문제"] -> 각 항목을 {title, guide:""} 로 변환.
"""

import json


class TemplateError(Exception):
    """양식 파일이 올바르지 않을 때 발생."""


def _normalize_section(item) -> dict | None:
    """
    한 항목을 {title, guide} 형태로 정규화.
    - 문자열이면 guide 없는 항목으로.
    - dict 면 title/guide 를 추출.
    - 제목이 비면 None (호출부에서 걸러짐).
    """
    if isinstance(item, str):
        title = item.strip()
        return {"title": title, "guide": ""} if title else None
    if isinstance(item, dict):
        title = str(item.get("title", "")).strip()
        guide = str(item.get("guide", "")).strip()
        return {"title": title, "guide": guide} if title else None
    return None


def load_template(file_bytes: bytes) -> dict:
    """
    업로드된 JSON 바이트를 읽어 {name, sections} 로 반환.
    sections 는 항상 {title, guide} dict 의 리스트입니다.
    형식이 잘못되면 TemplateError 를 던집니다.
    """
    try:
        data = json.loads(file_bytes.decode("utf-8"))
    except UnicodeDecodeError:
        raise TemplateError("파일 인코딩을 읽을 수 없습니다. UTF-8 JSON 파일인지 확인하세요.")
    except json.JSONDecodeError:
        raise TemplateError("JSON 형식이 올바르지 않습니다. 양식 파일이 손상되었을 수 있습니다.")

    if not isinstance(data, dict):
        raise TemplateError("양식 파일의 최상위는 객체(dict)여야 합니다.")

    raw_sections = data.get("sections")
    if not isinstance(raw_sections, list) or not raw_sections:
        raise TemplateError("양식에 'sections' 항목 목록이 있어야 합니다.")

    sections = []
    for item in raw_sections:
        norm = _normalize_section(item)
        if norm:
            sections.append(norm)

    if not sections:
        raise TemplateError("양식의 항목이 모두 비어 있습니다.")

    name = str(data.get("name", "")).strip() or "사용자 양식"
    return {"name": name, "sections": sections}


def export_template(name: str, sections: list) -> bytes:
    """
    양식을 다운로드 가능한 JSON 바이트로 변환.
    sections 는 {title, guide} dict 리스트 또는 문자열 리스트 모두 허용.
    """
    clean = []
    for item in sections:
        norm = _normalize_section(item)
        if norm:
            clean.append(norm)

    payload = {
        "name": (name or "사용자 양식").strip(),
        "sections": clean,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def sections_to_titles(sections) -> list:
    """일지 생성 시 사용할 항목 제목만 추출 (가이드는 프롬프트에서 별도 처리)."""
    titles = []
    for s in sections:
        if isinstance(s, dict):
            t = s.get("title", "").strip()
        else:
            t = str(s).strip()
        if t:
            titles.append(t)
    return titles


def sections_for_prompt(sections) -> str:
    """
    프롬프트에 넣을 항목 문자열 생성.
    가이드가 있으면 항목 옆에 괄호로 안내를 덧붙여 AI가 참고하게 함.
    """
    lines = []
    for i, s in enumerate(sections, start=1):
        if isinstance(s, dict):
            title = s.get("title", "").strip()
            guide = s.get("guide", "").strip()
        else:
            title, guide = str(s).strip(), ""
        if not title:
            continue
        if guide:
            lines.append(f"{i}. {title} — ({guide})")
        else:
            lines.append(f"{i}. {title}")
    return "\n".join(lines)
