import FinanceDataReader as fdr
import pandas as pd
import json

print("데이터 수집을 시작합니다... (약 1~2분 소요)")

# 1. 한국 주식 전 종목 가져오기 (KOSPI, KOSDAQ)
kr_stocks = fdr.StockListing('KRX')
# 필요한 컬럼만 선택
kr_stocks = kr_stocks[['Code', 'Name', 'Market']]

stock_list = []

# 한국 주식 데이터 변환
for idx, row in kr_stocks.iterrows():
    ticker = row['Code']
    # yfinance용 티커로 변환 (코스피: .KS, 코스닥: .KQ)
    if row['Market'] == 'KOSPI':
        ticker += ".KS"
    elif row['Market'] == 'KOSDAQ':
        ticker += ".KQ"
    
    stock_list.append({
        "ticker": ticker,
        "name_kr": row['Name'],
        "market": row['Market']
    })

print(f"한국 주식 {len(stock_list)}개 수집 완료.")

# 2. 미국 주식 (S&P 500) 가져오기
# 주의: 무료 API로는 '미국 주식의 한글명'을 완벽하게 가져오기 어렵습니다.
# 여기서는 S&P 500 종목을 가져오되, 주요 종목은 수동으로 한글 매핑을 하고 
# 나머지는 영어 이름을 그대로 사용하거나 티커를 보여주는 방식을 씁니다.

sp500 = fdr.StockListing('S&P500')

# 자주 찾는 미국 주식 한글 매핑 (필요한 만큼 추가하세요)
us_kor_map = {
    "AAPL": "애플", "MSFT": "마이크로소프트", "NVDA": "엔비디아", "TSLA": "테슬라",
    "GOOGL": "구글(알파벳A)", "GOOG": "구글(알파벳C)", "AMZN": "아마존",
    "META": "메타(페이스북)", "NFLX": "넷플릭스", "AMD": "AMD", "INTC": "인텔",
    "QCOM": "퀄컴", "TXN": "텍사스 인스트루먼트", "AVGO": "브로드컴",
    "AMAT": "어플라이드 머티어리얼즈", "MU": "마이크론", "SBUX": "스타벅스",
    "NKE": "나이키", "KO": "코카콜라", "MCD": "맥도날드", "DIS": "디즈니",
    "QQQ": "인베스코 QQQ (ETF)", "SPY": "SPDR S&P500 (ETF)", 
    "SOXL": "디렉시온 반도체 3배(ETF)", "TQQQ": "프로쉐어즈 나스닥 3배(ETF)"
}

count_us = 0
for idx, row in sp500.iterrows():
    ticker = row['Symbol']
    eng_name = row['Name']
    
    # 우리가 아는 한글 이름이 있으면 그걸 쓰고, 없으면 영어 이름 사용
    if ticker in us_kor_map:
        name_final = us_kor_map[ticker]
    else:
        name_final = eng_name # 한글 매핑 없는 건 영어 이름 그대로
        
    stock_list.append({
        "ticker": ticker,
        "name_kr": name_final,
        "market": "US"
    })
    count_us += 1

print(f"미국 주식 {count_us}개 수집 완료.")

# 3. JSON 파일로 저장
with open('stocks.json', 'w', encoding='utf-8') as f:
    json.dump(stock_list, f, ensure_ascii=False, indent=4)

print(f"총 {len(stock_list)}개 종목이 'stocks.json'에 저장되었습니다.")
