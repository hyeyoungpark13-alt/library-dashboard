import os
import json
import requests

def fetch_new_arrival_books():
    # 1. 환경변수에서 정보나루 API 인증키와 도서관 코드 가져오기
    auth_key = os.environ.get('LIBRARY_API_KEY')
    lib_code = os.environ.get('LIBRARY_CODE') # 도서관 코드를 환경변수에서 읽어옵니다.
    
    if not auth_key:
        print("❌ 에러: 환경변수 'LIBRARY_API_KEY'를 찾을 수 없습니다.")
        return
    if not lib_code:
        print("❌ 에러: 환경변수 'LIBRARY_CODE'를 찾을 수 없습니다. (예: 111001 등)")
        return

    # 2. 도서관 정보나루 신착도서(newArrivalBook) API URL 설정
    # pageSize=150으로 설정하여 최근 들어온 신착도서 상위 150권을 가져옵니다.
    url = "http://data4library.kr/api/newArrivalBook"
    params = {
        'authKey': auth_key,
        'libCode': lib_code,
        'pageSize': 150,
        'format': 'json'
    }

    print(f"📅 도서관 코드 {lib_code}의 신착도서 데이터를 조회합니다...")

    try:
        # 3. API 호출
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        res_data = response.json()
        docs = res_data.get('response', {}).get('docs', [])
        
        if not docs:
            print("⚠️ 경고: API 응답에 데이터가 없거나 인증키/도서관코드가 올바르지 않습니다.")
            return

        # 4. 신착도서 데이터 구조에 맞게 데이터 정제 (매핑)
        # 신착도서는 '대출건수' 대신 '권수' 정보 등이 포함되므로 대시보드 구조에 맞춰 가공합니다.
        processed_data = []
        for index, item in enumerate(docs):
            doc_info = item.get('doc', {})
            
            # 신착도서는 순위가 따로 안 오므로 배열 순서대로 1위, 2위... 임의 부여합니다.
            # 대출건수(loanCnt) 정보가 있다면 가져오고, 없으면 기본값 0 혹은 소장권수를 매핑합니다.
            loan_cnt = int(doc_info.get('loanCnt', 0)) if doc_info.get('loanCnt') else 0
            book_copies = int(doc_info.get('bookCopies', 1)) # 도서관이 소장한 권수
            
            book_item = {
                "rank": index + 1,                            # 임의 순위
                "title": doc_info.get('bookname', '정보 없음'), # 서명
                "author": doc_info.get('authors', '저자 없음'), # 저자
                "pub": doc_info.get('publisher', '출판사 없음'),# 출판사
                "copies": book_copies,                         # 차트 연동용 (소장 권수)
                "libs": loan_cnt                               # KPI 연동용 (현재까지의 대출 건수)
            }
            processed_data.append(book_item)

        # 최종 저장할 데이터 구조 생성 (신착도서 안내 문구 포함)
        final_output = {
            "period": f"최신 신착도서 분석 (도서관 코드: {lib_code})",
            "data": processed_data
        }

        # 5. 대시보드가 읽어갈 'data.json' 파일로 저장
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
            
        print("✅ 성공: 신착도서 기준 data.json 파일이 성공적으로 생성되었습니다!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    fetch_new_arrival_books()
