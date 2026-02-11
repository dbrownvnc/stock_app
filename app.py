import streamlit as st
from streamlit_searchbox import st_searchbox
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="주식 티커 자동완성", page_icon="⚡")

# 2. 데이터 준비
@st.cache_data
def load_data():
    # 실제 파일이 있으면 로드, 없으면 테스트 데이터 사용
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            stock_list = json.load(f)
    except:
        stock_list = [
            {"name_kr": "삼성전자", "ticker": "005930.KS"},
            {"name_kr": "SK하이닉스", "ticker": "000660.KS"},
            {"name_kr": "엔비디아", "ticker": "NVDA"},
            {"name_kr": "테슬라", "ticker": "TSLA"},
            {"name_kr": "애플", "ticker": "AAPL"},
            {"name_kr": "마이크로소프트", "ticker": "MSFT"},
            {"name_kr": "구글", "ticker": "GOOGL"},
            {"name_kr": "아마존", "ticker": "AMZN"},
            {"name_kr": "넷플릭스", "ticker": "NFLX"},
            {"name_kr": "카카오", "ticker": "035720.KS"},
            {"name_kr": "네이버", "ticker": "035420.KS"},
        ]
    return stock_list

stock_data = load_data()

# 3. 검색 로직 함수 (사용자가 타이핑할 때마다 실행됨)
def search_stock(searchterm: str):
    # 검색어가 없으면 빈 리스트 반환 (아무것도 안 보여줌)
    if not searchterm:
        return []
        
    searchterm = searchterm.lower().strip()
    results = []
    
    for stock in stock_data:
        # 한국어 이름이나 티커에 검색어가 포함되어 있으면 결과에 추가
        if searchterm in stock['name_kr'] or searchterm in stock['ticker'].lower():
            # (화면에 보일 이름, 실제 반환할 값) 튜플 형태로 저장
            label = f"{stock['name_kr']} ({stock['ticker']})"
            value = stock['ticker']
            results.append((label, value))
            
    return results

# --- UI 구현 ---

st.title("⚡ 주식 티커 자동완성")
st.markdown("입력창에 **'엔비'** 또는 **'삼성'**을 입력해보세요.")

# 4. 자동완성 입력창 (핵심)
# 사용자가 입력을 시작하면 search_stock 함수가 실행되어 리스트를 보여줍니다.
# 선택하면 selected_value 변수에 '티커(NVDA)'가 저장됩니다.
selected_ticker = st_searchbox(
    search_stock, 
    key="stock_search",
    placeholder="기업명 검색...",
    clear_on_submit=False, # 선택 후 입력창 내용을 유지
)

# 5. 결과 처리
if selected_ticker:
    st.divider()
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric(label="선택된 티커", value=selected_ticker)
    
    with col2:
        if st.button("차트 보기", key="chart_btn"):
            with st.spinner('데이터 로딩 중...'):
                try:
                    df = yf.download(selected_ticker, period="1mo", progress=False)
                    if not df.empty:
                        st.line_chart(df['Close'])
                    else:
                        st.error("데이터가 없습니다.")
                except Exception as e:
                    st.error(f"오류: {e}")

# (선택 사항) 디버깅용: 현재 상태 확인
# st.write(f"현재 입력된 값: {selected_ticker}")
