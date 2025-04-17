import re
import requests
from utils import xml_parser
import xml.etree.ElementTree as ET

OC = "chetera"
BASE = "http://www.law.go.kr"

def fetch_law_list_and_detail(query, unit):
    try:
        from urllib.parse import quote
        encoded_query = quote(f"{query}")
        url = f"{BASE}/DRF/lawSearch.do?OC={OC}&target=law&type=XML&display=10&search=2&knd=A0002&query={encoded_query}"
        print(f"[DEBUG] ▶ 법령목록 호출 URL: {url}")
        res = requests.get(url)
        res.encoding = "utf-8"
        if res.status_code != 200:
            return []

        root = ET.fromstring(res.content)
        terms = [t.strip() for t in re.split(r"[,&\-()]", query or "") if t.strip()]
        results = []

        for law in root.findall("law"):
            name = law.findtext("법령명한글", "").strip()
            mst = law.findtext("법령일련번호", "").strip()
            detail = law.findtext("법령상세링크", "").strip()
            full_link = BASE + detail
            xml_data = fetch_law_xml_by_mst(mst)
            if xml_data:
                print(f"[DEBUG] ▶ 본문 API 호출: {BASE + detail}")
                articles = xml_parser.parse_law_xml(xml_data, terms, unit)
                print(f"[DEBUG] ▶ 반한 조문 수 : {len(articles)}")
                if articles:
                    results.append({
                        "법령명한글": name,
                        "원문링크": full_link,
                        "조문": articles
                    })
        return results

    except Exception as e:
        import streamlit as st
        st.error(f"🚨 검색 중 오류 발생: {e}")
        return []

def fetch_law_xml_by_mst(mst):
    url = f"http://www.law.go.kr/DRF/lawService.do?OC={OC}&target=law&type=XML&mst={mst}"
    res = requests.get(url)
    res.encoding = "utf-8"
    print(f"[DEBUG] ▶ 법령 XML 호출 URL: {url}")
    print(f"[DEBUG] ▶ 응답 상태 코드: {res.status_code}")
    print(f"[DEBUG] ▶ 본문 일부:\n{res.text[:500]}")
    if res.status_code != 200:
        return None
    return res.text
