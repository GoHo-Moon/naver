import sys
import os
import urllib.request
import urllib.parse
import json
import pandas as pd
import re
from datetime import datetime

# my_apikeys.py가 같은 경로에 있다고 가정
sys.path.append('./') 
import my_apikeys as mykeys

def get_naver_news(keyword, num_data=1000):
    """
    네이버 뉴스 검색 API를 이용하여 뉴스를 수집하고 정리된 DataFrame을 반환하는 함수
    
    Args:
        keyword (str): 검색할 키워드 (예: "서울시 부동산")
        num_data (int): 수집할 기사 개수 (기본값 1000)
        
    Returns:
        pd.DataFrame: 수집된 뉴스 데이터 (pubDate, title, description, link)
    """
    
    # 1. 인증키 가져오기
    client_id = mykeys.naver_client_id
    client_secret = mykeys.naver_client_secret

    # 2. 파라미터 설정
    display_count = 100  # 한 페이지에 표시할 검색 결과 수
    sort = 'date'        # 정렬 기준 (date: 날짜순)
    
    # 검색어 URL 인코딩
    encText = urllib.parse.quote(keyword)
    
    results = []

    # 3. API 요청 및 데이터 수집
    # 1부터 num_data까지 display_count 간격으로 반복
    for idx in range(1, num_data + 1, display_count):
        url = "https://openapi.naver.com/v1/search/news?query=" + encText \
            + f"&start={idx}&display={display_count}&sort={sort}"
        
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        
        try:
            response = urllib.request.urlopen(request)
            rescode = response.getcode()
            
            if rescode == 200:
                response_body = response.read()
                response_dict = json.loads(response_body.decode('utf-8'))
                results.extend(response_dict['items']) # 리스트 확장
            else:
                print(f"Error Code: {rescode}")
                
        except Exception as e:
            print(f"요청 중 에러 발생: {e}")
            break # 에러 발생 시 중단

    print(f"'{keyword}' 검색 결과: 총 {len(results)}건 수집 완료")

    # 4. 데이터 전처리 및 DataFrame 변환
    if not results:
        return pd.DataFrame() # 결과가 없으면 빈 DF 반환

    # HTML 태그 제거용 정규표현식
    remove_tags = re.compile(r'<.*?>') 
    
    clean_data_list = []

    for item in results:
        try:
            # 날짜 변환 (Tue, 15 Dec 2025 10:00:00 +0900 형식 처리)
            pubDate_str = item['pubDate']
            pubDate_obj = datetime.strptime(pubDate_str, "%a, %d %b %Y %H:%M:%S +0900")
            
            # 태그 제거 및 특수문자 처리 (&quot; 등)
            title = re.sub(remove_tags, '', item['title']).replace("&quot;", '"').replace("&apos;", "'")
            description = re.sub(remove_tags, '', item['description']).replace("&quot;", '"').replace("&apos;", "'")
            
            # 리스트에 딕셔너리 형태로 추가
            clean_data_list.append({
                'pubDate': pubDate_obj,
                'title': title,
                'description': description,
                'link': item['link']
            })
        except Exception as e:
            continue # 변환 중 에러 발생 데이터는 건너뜀

    # 리스트를 한 번에 DataFrame으로 변환 (속도 최적화)
    df = pd.DataFrame(clean_data_list)
    
    return df

# 테스트용 코드 (api.py를 직접 실행했을 때만 동작)
if __name__ == "__main__":
    test_keyword = "인공지능"
    df_result = get_naver_news(test_keyword, 10) # 10개만 테스트
    print(df_result.head())
    # df_result.to_csv('test_result.csv', index=False, encoding='utf-8-sig')