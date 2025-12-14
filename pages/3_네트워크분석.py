import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm # 폰트 매니저 추가
from konlpy.tag import Okt
from itertools import combinations
from collections import Counter
import os # 파일 경로 확인용

# 1. 페이지 설정
st.set_page_config(page_title="키워드 네트워크 분석", page_icon="🕸️")

# 2. 데이터 가져오기 체크
if 'news_df' not in st.session_state:
    st.error("메인 페이지에서 먼저 데이터를 수집해주세요!")
else:
    df = st.session_state['news_df']
    keyword = st.session_state['search_keyword']
    
    st.title(f"🕸️ '{keyword}' 키워드 네트워크 분석")
    
    # ---------------------------------------------------------------------------
    # [수정 1] 폰트 설정: 프로젝트 내 ./fonts/ 폴더의 폰트 파일 강제 사용
    # ---------------------------------------------------------------------------
    font_path = "./fonts/AppleSDGothicNeoB.ttf"
    
    if os.path.exists(font_path):
        # 1. Matplotlib에 폰트 등록
        fm.fontManager.addfont(font_path)
        # 2. 등록된 폰트 이름 가져와서 설정
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc('font', family=font_name)
        plt.rc('axes', unicode_minus=False) # 마이너스 기호 깨짐 방지
    else:
        # 파일이 없을 경우 로컬 테스트용(Windows) 폰트 설정
        st.error(f"폰트 파일을 찾을 수 없습니다: {font_path}")
        plt.rc('font', family='Malgun Gothic')

    # [cite_start]3. 네트워크 데이터 생성 로직 (DV_14 강의록 10~11p) [cite: 2029-2041]
    with st.spinner("단어 관계를 분석 중입니다..."):
        okt = Okt()
        dataset = []
        
        # 제목+본문 리스트
        texts = (df['title'] + " " + df['description']).tolist()
        
        # ---------------------------------------------------------------------------
        # [수정 2] 불용어(Stopwords) 파일 불러오기 (./data/korean_stopwords.txt)
        # ---------------------------------------------------------------------------
        stopwords_path = "./data/korean_stopwords.txt"
        stop_words = []

        if os.path.exists(stopwords_path):
            with open(stopwords_path, 'r', encoding='utf-8') as f:
                stop_words = f.read().splitlines()
        else:
            st.warning(f"불용어 파일을 찾을 수 없습니다: {stopwords_path}")
            stop_words = ['것', '등', '위', '수', '배', '만', '명'] # 기본 불용어

        # 검색어(keyword)와 뉴스 상투어 추가
        stop_words.extend(['뉴스', '속보', '관련', '대해', keyword])

        # 각 기사별 명사 추출
        for text in texts:
            nouns = okt.nouns(text)
            refined = [n for n in nouns if len(n) > 1 and n not in stop_words]
            dataset.append(refined)
            
        # 엣지(Edge) 리스트 생성: 동시 등장 단어 쌍 구하기
        edge_list = []
        for doc in dataset:
            # 단어들의 조합(Combination) 생성 (순서 없음)
            for pair in combinations(doc, 2):
                edge_list.append(pair)
                
        # 엣지 빈도수 계산
        count = Counter(edge_list)
        
        # 상위 50개 관계만 추출
        top_edges = count.most_common(50) 

    # [cite_start]4. 그래프 생성 (DV_14 강의록 11p) [cite: 2063-2079]
    G = nx.Graph()
    
    for (u, v), weight in top_edges:
        G.add_edge(u, v, weight=weight)
        
    # [cite_start]5. 중심성 분석 (DV_14 강의록 8p) [cite: 1908-1912, 1922-1928]
    # 연결 중심성(Degree Centrality) 계산 -> 노드 크기에 반영
    centrality = nx.degree_centrality(G)
    
    # [cite_start]6. 네트워크 시각화 (DV_14 강의록 12p) [cite: 2083-2127]
    if len(top_edges) == 0:
        st.warning("연관된 단어 관계를 찾을 수 없습니다.")
    else:
        fig, ax = plt.subplots(figsize=(12, 12))
        
        # 레이아웃 결정 (spring_layout: 힘 기반 배치)
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # 노드 크기 설정 (중심성에 비례하여 키움)
        node_size = [v * 5000 for v in centrality.values()]
        
        # 엣지 두께 설정 (가중치에 비례)
        edge_width = [d['weight'] * 0.2 for (u, v, d) in G.edges(data=True)]

        nx.draw_networkx(
            G, 
            pos,
            with_labels=True,
            node_size=node_size,
            node_color="skyblue",
            edge_color="gray",
            width=edge_width,
            # [중요] 위에서 설정한 폰트 적용 (파일이 없으면 Malgun Gothic 사용)
            font_family=font_name if os.path.exists(font_path) else 'Malgun Gothic', 
            font_size=12,
            alpha=0.8
        )
        
        plt.axis('off') # 축 제거
        st.pyplot(fig)
        
        st.info("""
        **💡 시각화 해석 가이드**
        * **노드(점) 크기**: 연결 중심성 (다른 단어들과 얼마나 많이 연결되었는지)
        * **선(Edge) 두께**: 동시 등장 빈도 (두 단어가 기사에서 함께 나온 횟수)
        """)