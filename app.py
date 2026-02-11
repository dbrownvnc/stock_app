import streamlit as st
from streamlit_searchbox import st_searchbox
import json
import yfinance as yf

# 1. 데이터 로드 (캐싱)
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
            {"name_kr": "애플", "ticker": "AAPL"}
        ]

stock_list = load_stock_data()

# 2. 검색 로직 (label과 value 분리)
def search_stocks(searchterm: str):
    if not searchterm:
        return []
    
    searchterm = searchterm.lower().strip()
    results = []
    
    for stock in stock_list:
        if searchterm in stock['name_kr'].lower() or searchterm in stock['ticker'].lower():
            # 사용자가 보는 것: 이름 (티커) / 실제 값: 티커
            label = f"{stock['name_kr']} ({stock['ticker']})"
            value = stock['ticker']
            results.append((label, value))
            
    return results

# --- UI 구현 ---

st.title("🔍 티커 자동완성 검색기")

# 3. 핵심 위젯: st_searchbox
# edit_after_submit=True를 사용하되, 반환된 값을 즉시 변수에 담습니다.
selected_ticker = st_searchbox(
    search_stocks,
    key="ticker_search",
    placeholder="기업명을 입력하세요...",
    edit_after_submit=True,
)

# 4. 결과 출력 및 오류 방지 로직
if selected_ticker:
    # 검증: 리스트에 존재하는 티커인지 확인
    is_valid = any(s['ticker'] == selected_ticker for s in stock_list)
    
    if is_valid:
        st.divider()
        try:
            with st.spinner(f"'{selected_ticker}' 데이터를 불러오는 중..."):
                # 데이터 다운로드
                df = yf.download(selected_ticker, period="1mo", progress=False)
                
                if not df.empty:
                    st.subheader(f"📊 {selected_ticker} 차트 분석")
                    st.line_chart(df['Close'])
                    
                    # [오류 수정 포인트] Series에서 마지막 종가(단일 숫자)만 추출
                    # iloc[-1]을 한 뒤 .item()을 사용하거나 float()으로 변환하여 포맷팅 오류 방지
                    last_price_val = float(df['Close'].iloc[-1])
                    
                    st.metric("최근 종가", f"{last_price_val:,.2f}")
                else:
                    st.error("데이터를 찾을 수 없는 티커입니다.")
        except Exception as e:
            # 상세 오류 메시지 출력 (디버깅용)
            st.error(f"데이터 처리 중 오류 발생: {e}")
    else:
        # 리스트에서 선택하지 않고 텍스트만 남아있는 경우 안내
        if "(" in selected_ticker:
             st.info("리스트에서 종목을 정확히 클릭해 주세요.")

st.info("💡 **동작 검증**: 선택 시 입력창에는 티커만 남으며, 클릭 시 즉시 재검색이 가능합니다.")
