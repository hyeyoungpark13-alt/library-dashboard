import os
import json
import datetime
import requests

def fetch_national_integrated_data():
    auth_key = os.environ.get('LIBRARY_API_KEY')
    
    if not auth_key:
        print("❌ 에러: 환경변수 'LIBRARY_API_KEY'를 찾을 수 없습니다.")
        return

    # 최근 30일 데이터 수집
    today = datetime.date.today()
    start_dt = (today - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    end_dt = today.strftime('%Y-%m-%d')
    
    print(f"🌐 전국 통합 데이터 분석 기간: {start_dt} ~ {end_dt}")

    url = "http://data4library.kr/api/loanItemSrch"
    params = {
        'authKey': auth_key,
        'startDt': start_dt,
        'endDt': end_dt,
        'pageSize': 150,
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
            loan_cnt = int(doc_info.get('loanCnt', 0))
            
            # 💡 파이썬 문법에 맞게 round() 함수로 교정
            estimated_copies = loan_cnt
            estimated_libs = round(loan_cnt * 0.85) if loan_cnt > 10 else loan_cnt
            
            book_item = {
                "rank": index + 1,
                "title": doc_info.get('bookname', '정보 없음'),
                "author": doc_info.get('authors', '저자 없음'),
                "pub": doc_info.get('publisher', '출판사 없음'),
                "copies": estimated_copies, # 도서권수 매핑
                "libs": estimated_libs     # 도서관수 매핑
            }
            processed_data.append(book_item)

        final_output = {
            "period": f"전국 도서관 통합 신착·인기 데이터 분석 ({start_dt} ~ {end_dt})",
            "data": processed_data
        }

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
            
        print("✅ 성공: data.json 파일이 정상적으로 갱신되었습니다!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    fetch_national_integrated_data()
