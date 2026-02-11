import streamlit as st
from streamlit_searchbox import st_searchbox
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="Ticker Only Search", layout="centered")

# 2. 데이터 로드 (stocks.json 활용)
@st.cache_data
def load_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # 데이터가 없을 경우를 대비한 샘플
        return [
            {"name_kr": "삼성전자", "ticker": "005930.KS"},
            {"name_kr": "엔비디아", "ticker": "NVDA"},
            {"name_kr": "테슬라", "ticker": "TSLA"},
            {"name_kr": "애플", "ticker": "AAPL"},
            {"name_kr": "마이크로소프트", "ticker": "MSFT"}
        ]

stock_list = load_data()

# 3. 검색 로직 함수
def search_stock(searchterm: str):
    if not searchterm:
        return []
    
    searchterm = searchterm.lower().strip()
    results = []
    
    for stock in stock_list:
        # 한글명이나 티커로 검색 가능
        if searchterm in stock['name_kr'] or searchterm in stock['ticker'].lower():
            # [중요] (화면에 보여줄 문구, 실제로 입력창에 남길 값)
            # 여기를 (이름+티커, 티커) 순으로 설정하여 선택 시 티커만 남게 합니다.
            label = f"{stock['name_kr']} ({stock['ticker']})"
            value = stock['ticker']
            results.append((label, value))
            
    return results

# --- UI 구현 ---

st.title("🔍 티커 자동완성 검색기")
st.write("선택 즉시 **티커**만 남으며, 언제든 다시 입력하여 검색할 수 있습니다.")

# 4. 핵심 위젯: st_searchbox
# edit_after_submit=True: 선택 후에도 텍스트가 확정되지 않고 바로 수정 가능 모드 유지
selected_ticker = st_searchbox(
    search_stock,
    key="ticker_search_box",
    placeholder="기업명 입력 (예: 삼성, 엔비...)",
    edit_after_submit=True, 
)

# 5. 결과 분석 (차트)
if selected_ticker:
    st.divider()
    try:
        # yfinance로 주가 데이터 가져오기
        df = yf.download(selected_ticker, period="1mo", progress=False)
        
        if not df.empty:
            st.subheader(f"📊 {selected_ticker} 최근 한 달 차트")
            st.line_chart(df['Close'])
            
            # 정보 요약 (Metric)
            last_price = df['Close'].iloc[-1]
            st.metric("최근 종가", f"{last_price:,.2f}")
        else:
            # 사용자가 티커가 아닌 텍스트를 입력하고 엔터를 쳤을 경우 대비
            st.warning("유효한 티커를 선택해 주세요.")
            
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다.")

st.caption("💡 팁: 입력창에 티커가 남아있어도 바로 지우거나 타이핑하면 즉시 재검색이 시작됩니다.")
