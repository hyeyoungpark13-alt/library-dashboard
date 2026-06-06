import os
import json
import datetime
import requests

def fetch_library_data():
    # 1. 환경변수에서 정보나루 API 인증키 가져오기
    # GitHub Actions 설정 시 'LIBRARY_API_KEY'라는 이름으로 등록해야 합니다.
    auth_key = os.environ.get('LIBRARY_API_KEY')
    
    if not auth_key:
        print("❌ 에러: 환경변수 'LIBRARY_API_KEY'를 찾을 수 없습니다.")
        return

    # 2. 조회할 '지난달' 날짜 계산하기
    # API 특성상 당월(이번 달)은 데이터가 누적 중이므로, 직전 달(완성된 데이터)을 가져오는 것이 가장 정확합니다.
    today = datetime.date.today()
    first_day_of_this_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_this_month - datetime.timedelta(days=1)
    
    year = last_day_of_last_month.year
    month = f"{last_day_of_last_month.month:02d}" # 예: 5 -> '05'
    
    start_dt = f"{year}-{month}-01"
    end_dt = f"{year}-{month}-{last_day_of_last_month.day:02d}"
    
    print(f"📅 데이터 조회 기간: {start_dt} ~ {end_dt}")

    # 3. 도서관 정보나루 인기대출도서(loanItemSrch) API URL 설정
    # pageSize=150으로 설정하여 상위 150권의 데이터를 가져옵니다.
    url = "http://data4library.kr/api/loanItemSrch"
    params = {
        'authKey': auth_key,
        'startDt': start_dt,
        'endDt': end_dt,
        'pageSize': 150,
        'format': 'json'
    }

    try:
        # 4. API 호출
        response = requests.get(url, params=params)
        response.raise_for_status() # 통신 에러 발생 시 예외 처리
        
        res_data = response.json()
        docs = res_data.get('response', {}).get('docs', [])
        
        if not docs:
            print("⚠️ 경고: API 응답에 데이터가 없거나 인증키가 올바르지 않습니다.")
            return

        # 5. 기존 HTML 대시보드 규격에 맞게 데이터 정제 (매핑)
        processed_data = []
        for index, item in enumerate(docs):
            doc_info = item.get('doc', {})
            
            # 대출건수를 숫자로 안전하게 변환 (없으면 0)
            loan_cnt = int(doc_info.get('loanCnt', 0))
            
            book_item = {
                "rank": index + 1,                            # 순위 (1부터 시작)
                "title": doc_info.get('bookname', '정보 없음'), # 서명
                "author": doc_info.get('authors', '화자 없음'), # 저자
                "pub": doc_info.get('publisher', '출판사 없음'),# 출판사
                "copies": loan_cnt,                            # 대출건수 (대시보드 차트 연동용)
                "libs": loan_cnt                               # 대출건수 (대시보드 KPI 연동용)
            }
            processed_data.append(book_item)

        # 최종 저장할 데이터 구조 생성 (조회 기준월 정보 포함)
        final_output = {
            "period": f"{year}년 {month}월 데이터 (정기 자동 업데이트)",
            "data": processed_data
        }

        # 6. 대시보드가 읽어갈 'data.json' 파일로 저장
        # ensure_ascii=False를 해야 한글이 깨지지 않고 올바르게 기록됩니다.
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
            
        print("✅ 성공: data.json 파일이 성공적으로 생성 및 갱신되었습니다!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    fetch_library_data()