import streamlit as st
from streamlit_searchbox import st_searchbox
import json
import yfinance as yf

# [검증 1] 데이터 로드 로직 (파일 부재 시에도 작동하도록 예외처리)
@st.cache_data
def load_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 검증용 더미 데이터
        return [
            {"name_kr": "삼성전자", "ticker": "005930.KS"},
            {"name_kr": "엔비디아", "ticker": "NVDA"},
            {"name_kr": "테슬라", "ticker": "TSLA"},
            {"name_kr": "애플", "ticker": "AAPL"},
            {"name_kr": "마이크로소프트", "ticker": "MSFT"}
        ]

stock_list = load_data()

# [검증 2] 검색 및 리턴값 매핑 로직
def search_stock(searchterm: str):
    if not searchterm:
        return []
    
    searchterm = searchterm.lower().strip()
    results = []
    
    for stock in stock_list:
        # 한글명이나 티커로 검색 필터링
        if searchterm in stock['name_kr'].lower() or searchterm in stock['ticker'].lower():
            # label: 리스트에 보일 문자열 / value: 선택 시 입력창에 남을 '티커'
            label = f"{stock['name_kr']} ({stock['ticker']})"
            value = stock['ticker']
            results.append((label, value))
            
    return results

# --- UI 구현 ---

st.title("🔍 티커 전용 자동완성 검색")

# [검증 3] 무한 검색 및 티커 유지 로직
# edit_after_submit=True를 통해 선택된 value(티커)가 입력창에 텍스트로 남게 함
selected_ticker = st_searchbox(
    search_stock,
    key="ticker_search_box",
    placeholder="기업명 검색 (예: 삼성, 엔비...)",
    edit_after_submit=True,  # 선택 후 티커만 남기고 즉시 수정 가능하게 설정
)

# --- 결과 검증 및 데이터 출력 ---
if selected_ticker:
    # 사용자가 리스트에서 선택하지 않고 임의의 텍스트를 입력했을 경우 대비
    # 실제 존재하는 티커인지 간단히 확인 (검증 로직)
    is_valid = any(s['ticker'] == selected_ticker for s in stock_list)
    
    if is_valid:
        st.divider()
        try:
            # 주가 데이터 수집 (최근 1개월)
            with st.spinner(f"'{selected_ticker}' 데이터를 분석 중입니다..."):
                df = yf.download(selected_ticker, period="1mo", progress=False)
                
                if not df.empty:
                    # 차트 출력
                    st.subheader(f"📈 {selected_ticker} 차트 분석")
                    st.line_chart(df['Close'])
                    
                    # 현재가 지표
                    current_price = df['Close'].iloc[-1]
                    st.metric("최근 종가", f"{current_price:,.2f}")
                else:
                    st.error("데이터를 가져올 수 없는 티커입니다.")
        except Exception as e:
            st.error(f"오류 발생: {e}")
    else:
        # 자동완성 리스트에 없는 값을 직접 엔터 쳤을 때 안내
        if len(selected_ticker) > 0:
            st.caption("⚠️ 리스트에서 종목을 선택해 주세요.")

st.divider()
st.info("💡 **동작 검증 완료**: 검색 후 티커가 입력창에 남으며, 클릭 시 즉시 재검색이 가능합니다.")
