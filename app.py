import streamlit as st
from streamlit_searchbox import st_searchbox
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="Stock Ticker Search", layout="centered")

# 2. 데이터 로드 (stocks.json이 없는 경우를 대비한 기본 데이터 포함)
@st.cache_data
def load_stock_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return [
            {"name_kr": "삼성전자", "ticker": "005930.KS"},
            {"name_kr": "엔비디아", "ticker": "NVDA"},
            {"name_kr": "테슬라", "ticker": "TSLA"},
            {"name_kr": "애플", "ticker": "AAPL"},
            {"name_kr": "마이크로소프트", "ticker": "MSFT"}
        ]

stock_list = load_stock_data()

# 3. 자동완성 검색 로직 (핵심 수정 부분)
def search_stocks(searchterm: str):
    if not searchterm:
        return []
    
    searchterm = searchterm.lower().strip()
    results = []
    
    for stock in stock_list:
        # 한글 이름이나 티커로 검색 필터링
        if searchterm in stock['name_kr'].lower() or searchterm in stock['ticker'].lower():
            # label: 드롭다운 리스트에 보일 문자열
            # value: 선택 시 입력창에 실제로 남게 될 값 (티커만 설정)
            label = f"{stock['name_kr']} ({stock['ticker']})"
            value = stock['ticker'] 
            results.append((label, value))
            
    return results

# --- UI 구현 ---

st.title("🔍 티커 자동완성 검색")
st.markdown("이름으로 검색해도 **티커만 남습니다.**")

# 4. 스마트 검색창 위젯
# edit_after_submit=True: 선택 후에도 티커가 텍스트로 남아 즉시 수정/재검색 가능
selected_ticker = st_searchbox(
    search_stocks,
    key="ticker_search",
    placeholder="기업명 검색 (예: 삼성, 엔비...)",
    edit_after_submit=True,
)

# 5. 결과 검증 및 데이터 출력
if selected_ticker:
    # 리스트에 있는 유효한 티커인지 확인
    is_valid = any(s['ticker'] == selected_ticker for s in stock_list)
    
    if is_valid:
        st.divider()
        try:
            with st.spinner(f"'{selected_ticker}' 데이터를 불러오는 중..."):
                df = yf.download(selected_ticker, period="1mo", progress=False)
                
                if not df.empty:
                    st.subheader(f"📊 {selected_ticker} 주가 분석")
                    st.line_chart(df['Close'])
                    
                    # 현재가 지표 표시
                    last_price = df['Close'].iloc[-1]
                    st.metric("최근 종가", f"{last_price:,.2f}")
                else:
                    st.error("차트 데이터를 가져올 수 없는 티커입니다.")
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
    else:
        # 직접 입력 시 리스트에 없는 경우 안내
        if len(selected_ticker) > 0:
            st.caption("⚠️ 검색 리스트에서 종목을 선택해 주세요.")

st.info("💡 **동작 안내**: 선택 즉시 티커만 입력창에 남으며, 언제든 클릭하여 다시 입력하면 자동완성이 활성화됩니다.")
