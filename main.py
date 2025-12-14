import streamlit as st
import pandas as pd
import api  # 우리가 만든 api.py

# 1. 페이지 기본 설정 (가장 먼저 실행되어야 함)
st.set_page_config(
    page_title="이슈 파인더(Issue Finder)",
    page_icon="🔍",
    layout="wide"
)

# 2. [고급 기능] 캐싱 적용 (@st.cache_data) 
# 동일한 검색어와 개수로 호출되면, 저장된 결과를 즉시 반환합니다.
@st.cache_data
def fetch_news_data(keyword, num):
    return api.get_naver_news(keyword, num)

# 3. 사이드바 구성
with st.sidebar:
    st.header("⚙️ 설정 및 안내")
    st.info("이곳은 메인 페이지입니다.")
    st.markdown("---")
    st.write("다른 페이지로 이동하여 시각화를 확인하세요.")

# 4. 메인 화면 구성
st.title("🗣️ 소셜 미디어 여론 분석 대시보드")
st.markdown("""
### 🔍 이슈 키워드 검색
네이버 뉴스 데이터를 수집하여 **워드클라우드** 및 **네트워크 분석**을 수행합니다.
검색어를 입력하고 버튼을 눌러주세요.
""")
st.divider()

# 레이아웃 분할 (입력창과 버튼 정렬)
col1, col2 = st.columns([4, 1])

with col1:
    keyword = st.text_input("검색어 입력", placeholder="예: 서울시 부동산, 인공지능, 기후변화")

with col2:
    st.write("") # 높이 맞추기용 공백
    st.write("")
    # 버튼 클릭
    search_btn = st.button("데이터 수집 시작 🚀", use_container_width=True)

# 5. [고급 기능] 세션 상태를 활용한 데이터 처리 
if search_btn:
    if not keyword:
        st.warning("검색어를 입력해주세요!")
    else:
        with st.spinner(f"'{keyword}' 관련 뉴스를 네이버에서 수집 중입니다..."):
            try:
                # 캐싱된 함수 호출 (속도 향상)
                df = fetch_news_data(keyword, 1000)
                
                if not df.empty:
                    # [핵심] 수집된 데이터를 세션 상태(st.session_state)에 저장
                    # 이렇게 해야 다른 페이지(시각화)로 이동해도 데이터가 유지됩니다.
                    st.session_state['news_df'] = df
                    st.session_state['search_keyword'] = keyword
                    
                    st.success(f"수집 완료! 총 {len(df)}개의 기사를 가져왔습니다.")
                else:
                    st.warning("검색 결과가 없습니다.")
            except Exception as e:
                st.error(f"에러 발생: {e}")

# 6. 수집된 데이터가 있다면 화면에 표시 (버튼을 안 눌러도 데이터가 있으면 표시)
if 'news_df' in st.session_state and not st.session_state['news_df'].empty:
    st.markdown(f"### 📊 '{st.session_state['search_keyword']}' 검색 결과 미리보기")
    
    # 데이터프레임 출력 (확장 컨테이너 사용)
    with st.expander("원본 데이터 확인하기", expanded=True):
        st.dataframe(st.session_state['news_df'])
    
    st.info("💡 왼쪽 사이드바에서 **시각화 페이지**로 이동하면 상세 분석 결과를 볼 수 있습니다.")