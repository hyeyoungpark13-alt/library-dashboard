import os
import json
import datetime
import requests

def fetch_national_integrated_data():
    # 1. 환경변수에서 API 인증키 가져오기 (도서관 코드는 이제 필요 없음)
    auth_key = os.environ.get('LIBRARY_API_KEY')
    
    if not auth_key:
        print("❌ 에러: 환경변수 'LIBRARY_API_KEY'를 찾을 수 없습니다.")
        return

    # 2. 조회할 기간 설정 (최근 1개월 동안 전국 도서관에 입고/활성화된 신착 기준)
    today = datetime.date.today()
    start_dt = (today - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    end_dt = today.strftime('%Y-%m-%d')
    
    print(f"🌐 전국 도서관 통합 데이터 분석 기간: {start_dt} ~ {end_dt}")

    # 3. 전국 통합 대출/소장 현황을 판단할 수 있는 loanItemSrch API 사용 (libCode 제외 시 전국 통합)
    url = "http://data4library.kr/api/loanItemSrch"
    params = {
        'authKey': auth_key,
        'startDt': start_dt,
        'endDt': end_dt,
        'pageSize': 150, # 상위 150권 추출
        'format': 'json'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        res_data = response.json()
        docs = res_data.get('response', {}).get('docs', [])
        
        if not docs:
            print("⚠️ 경고: API 응답에 데이터가 없습니다.")
            return

        processed_data = []
        for index, item in enumerate(docs):
            doc_info = item.get('doc', {})
            
            # 💡 엑셀 파일의 '도서권수'와 '도서관수' 개념을 API 데이터와 매핑합니다.
            # 정보나루 전국 데이터에서는 대출건수(loanCnt)를 기반으로 전국 인프라 확산도를 산출합니다.
            loan_cnt = int(doc_info.get('loanCnt', 0))
            
            # 전국 통합 데이터 규격으로 변환 (올려주신 엑셀 구조 반영)
            book_item = {
                "rank": index + 1,                            # 순위
                "title": doc_info.get('bookname', '정보 없음'), # 서명
                "author": doc_info.get('authors', '저자 없음'), # 저자
                "pub": doc_info.get('publisher', '출판사 없음'),# 출판사
                "copies": loan_cnt,                            # 대시보드 그래프용 (도서 총 이용 규모)
                "libs": Math.round(loan_cnt * 0.9) if loan_cnt > 10 else loan_cnt # 전국 확산 도서관 수 추정치 계산
            }
            processed_data.append(book_item)

        final_output = {
            "period": f"전국 도서관 통합 신착·인기 도서 분석 ({start_dt} ~ {end_dt} 기준)",
            "data": processed_data
        }

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
            
        print("✅ 성공: 전국 통합 data.json 파일이 성공적으로 생성되었습니다!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    fetch_national_integrated_data()
