import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wordcloud import WordCloud
from konlpy.tag import Okt
from collections import Counter
import os # 파일 경로 확인용
import numpy as np
from PIL import Image

# 1. 페이지 설정
st.set_page_config(page_title="워드클라우드 분석", page_icon="☁️")

# 2. 데이터 확인
if 'news_df' not in st.session_state:
    st.error("메인 페이지에서 먼저 데이터를 수집해주세요!")
else:
    df = st.session_state['news_df']
    keyword = st.session_state['search_keyword']

    st.title(f"☁️ '{keyword}' 뉴스 워드클라우드")
    
    # ---------------------------------------------------------------------------
    # [폰트 설정] 프로젝트 내 ./fonts/ 폴더의 폰트 파일 사용
    # ---------------------------------------------------------------------------
    font_path = "./fonts/AppleSDGothicNeoB.ttf"
    
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc('font', family=font_name)
        plt.rc('axes', unicode_minus=False)
    else:
        st.error(f"폰트 파일을 찾을 수 없습니다: {font_path}")
        font_path = "c:/Windows/Fonts/malgun.ttf"
        plt.rc('font', family='Malgun Gothic')

    # 3. 텍스트 분석
    with st.spinner("텍스트를 분석하고 있습니다..."):
        okt = Okt()
        
        text_data = df['title'] + " " + df['description']
        all_text = " ".join(text_data.tolist())

        nouns = okt.nouns(all_text)
        
        # ---------------------------------------------------------------------------
        # [수정] 불용어(Stopwords) 파일 불러오기 (data/korean_stopwords.txt)
        # ---------------------------------------------------------------------------
        # Streamlit 실행 위치 기준 경로: ./data/korean_stopwords.txt
        stopwords_path = "./data/korean_stopwords.txt"
        stop_words = []

        if os.path.exists(stopwords_path):
            # 파일이 있으면 읽어서 리스트로 변환
            with open(stopwords_path, 'r', encoding='utf-8') as f:
                stop_words = f.read().splitlines()
        else:
            # 파일이 없으면 경고 메시지 출력
            st.warning(f"불용어 파일을 찾을 수 없습니다: {stopwords_path}")
            stop_words = ['것', '등', '위', '수', '배', '만', '명'] # 기본 불용어

        # 검색어(keyword)와 뉴스 상투어 추가
        stop_words.extend(['뉴스', '속보', '관련', '대해', keyword])
        
        # 명사 필터링 (불용어 제거 + 2글자 이상)
        refined_nouns = [n for n in nouns if len(n) > 1 and n not in stop_words]
        
        count = Counter(refined_nouns)
        most_common_words = count.most_common(50)

    # 4. 워드클라우드 생성

    # 마스크 이미지 불러오기 및 변환 (경로 수정 필요)
    mask_path = "../data/mask.png" 
#    cross_mask.png 파일을 PIL Image로 읽고 numpy 배열로 변환
    try:
        mask_image = np.array(Image.open(mask_path).convert("RGB")) 
    except FileNotFoundError:
        st.warning(f"마스크 파일을 찾을 수 없습니다: {mask_path}. 기본 모양으로 출력합니다.")
        mask_image = None

if not refined_nouns:
    st.warning("분석할 텍스트가 부족합니다.")
else:
    wc = WordCloud(
        font_path=font_path,
        background_color='black', # 마스크 적용 시 배경색을 검정으로 하면 더 깔끔할 수 있습니다.
        width=800,
        height=600,
        colormap='coolwarm', # 한글 워드클라우드 예시에서 사용한 'coolwarm'도 좋습니다[cite: 1751].
        max_words=50,
        mask=mask_image # <<-- 여기에 마스크 적용!
    ).generate_from_frequencies(dict(most_common_words))
    if not refined_nouns:
        st.warning("분석할 텍스트가 부족합니다.")
    else:
        wc = WordCloud(
            font_path=font_path,      # 폰트 경로 적용
            background_color='white',
            width=800,
            height=600,
            colormap='viridis',
            max_words=50
        ).generate_from_frequencies(dict(most_common_words))

        # 5. 화면 출력
        fig = plt.figure(figsize=(10, 6))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(fig)
        
        with st.expander("단어 빈도수 데이터 보기"):
            st.dataframe(pd.DataFrame(most_common_words, columns=['단어', '빈도수']))
