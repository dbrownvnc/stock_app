import streamlit as st
from streamlit_searchbox import st_searchbox
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="무한 자동완성 검색기", layout="centered")

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
            {"name_kr": "애플", "ticker": "AAPL"}
        ]

stock_list = load_data()

# 3. 검색 로직 함수 (사용자가 타이핑할 때마다 실행)
def search_stock(searchterm: str):
    # 입력이 없으면 결과 없음
    if not searchterm:
        return []
    
    searchterm = searchterm.lower().strip()
    results = []
    
    for stock in stock_list:
        # 이름이나 티커에 검색어 포함 시 리스트에 추가
        if searchterm in stock['name_kr'] or searchterm in stock['ticker'].lower():
            # (화면에 보일 이름, 실제 반환할 티커값)
            label = f"{stock['name_kr']} ({stock['ticker']})"
            value = stock['ticker']
            results.append((label, value))
            
    return results

# --- UI 구현 ---

st.title("📈 통합 스마트 검색창")
st.write("이미 입력된 상태에서도 **바로 타이핑**하면 자동완성이 시작됩니다.")

# 4. 핵심 위젯: st_searchbox
# edit_after_submit=True 설정으로 선택 후에도 즉시 재수정이 가능하게 만듭니다.
selected_ticker = st_searchbox(
    search_stock,
    key="stock_search",
    placeholder="기업명 또는 티커 입력...",
    edit_after_submit=True, # ★ 선택 후에도 클릭 즉시 수정/검색 가능하게 하는 핵심 옵션
)

# 5. 결과 분석 (차트)
if selected_ticker:
    st.divider()
    # 입력창 바로 아래 분석 결과 노출
    try:
        df = yf.download(selected_ticker, period="1mo", progress=False)
        if not df.empty:
            st.subheader(f"📊 {selected_ticker} 주가 분석")
            st.line_chart(df['Close'])
            
            # 현재가 정보 표시
            last_price = df['Close'].iloc[-1]
            st.metric("현재 종가", f"{last_price:,.2f}")
        else:
            st.error("데이터를 가져올 수 없는 종목입니다.")
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")

st.caption("💡 팁: 티커가 완성된 상태에서도 입력창을 클릭하고 바로 다른 기업명을 검색해 보세요.")
