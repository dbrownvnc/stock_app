import streamlit as st
from streamlit_searchbox import st_searchbox
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="Ticker Auto-Complete", layout="centered")

# 2. 데이터 로드 (stocks.json 활용)
@st.cache_data
def load_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 테스트용 더미 데이터
        return [
            {"name_kr": "삼성전자", "ticker": "005930.KS"},
            {"name_kr": "엔비디아", "ticker": "NVDA"},
            {"name_kr": "테슬라", "ticker": "TSLA"},
            {"name_kr": "애플", "ticker": "AAPL"},
            {"name_kr": "마이크로소프트", "ticker": "MSFT"}
        ]

stock_list = load_data()

# 3. 검색 로직
def search_stock(searchterm: str):
    if not searchterm:
        return []
    
    searchterm = searchterm.lower().strip()
    results = []
    
    for stock in stock_list:
        if searchterm in stock['name_kr'].lower() or searchterm in stock['ticker'].lower():
            # 검색 리스트에는 '이름 (티커)' 형태로 친절하게 보여줌
            label = f"{stock['name_kr']} ({stock['ticker']})"
            value = stock['ticker']
            results.append((label, value))
            
    return results

# --- 상태 관리 (세션 스테이트) ---
if 'search_mode' not in st.session_state:
    st.session_state['search_mode'] = True  # True: 검색창 / False: 결과창
if 'selected_ticker' not in st.session_state:
    st.session_state['selected_ticker'] = ""

# 검색창에서 값을 선택했을 때 실행
def on_search_submit(value):
    if value:
        st.session_state['selected_ticker'] = value
        st.session_state['search_mode'] = False # 결과창 모드로 전환
        # st.rerun()은 st_searchbox 내부 로직과 충돌할 수 있으므로 상태만 변경

# 결과창(티커)을 수정하려고 할 때 실행
def on_result_change():
    st.session_state['search_mode'] = True # 다시 검색 모드로 전환
    st.session_state['selected_ticker'] = ""

# --- UI 구현 (같은 위치에서 위젯 교체) ---

st.title("📈 주식 티커 검색기")
st.markdown("이름으로 검색하면 **티커**만 입력됩니다.")

# 위젯이 표시될 컨테이너
search_container = st.empty()

# [모드 A] 검색 중일 때 (st_searchbox 표시)
if st.session_state['search_mode']:
    with search_container:
        # 1. 검색 위젯
        new_selection = st_searchbox(
            search_stock,
            key="stock_searchbox",
            placeholder="기업명 검색 (예: 삼성, 엔비...)",
            # 키가 바뀌면 위젯이 초기화되므로 고정 키 사용
        )
        
        # 2. 선택 감지 및 모드 전환 로직
        if new_selection and new_selection != st.session_state.get('last_selection'):
            st.session_state['selected_ticker'] = new_selection
            st.session_state['search_mode'] = False
            st.session_state['last_selection'] = new_selection
            st.rerun() # 화면 새로고침하여 text_input으로 교체

# [모드 B] 선택 완료 시 (st.text_input 표시)
else:
    with search_container:
        st.text_input(
            "Ticker",
            value=st.session_state['selected_ticker'],
            key="result_ticker_input",
            on_change=on_result_change, # 텍스트를 건드리면 즉시 검색모드로 복귀
            label_visibility="collapsed"
        )
        st.caption("✅ 티커 입력 완료. (수정하려면 위 텍스트를 지우세요)")

# --- 결과 분석 및 오류 수정 ---
final_ticker = st.session_state['selected_ticker']

if final_ticker and not st.session_state['search_mode']:
    st.divider()
    try:
        # 데이터 가져오기
        df = yf.download(final_ticker, period="1mo", progress=False)
        
        if not df.empty:
            st.subheader(f"📊 {final_ticker} 차트")
            st.line_chart(df['Close'])
            
            # [오류 수정] Series 포맷팅 문제 해결
            # iloc[-1]로 값을 가져온 뒤 .item()을 호출하여 순수 파이썬 float로 변환
            last_close = df['Close'].iloc[-1]
            try:
                price_val = last_close.item() 
            except:
                price_val = float(last_close)
                
            st.metric("최근 종가", f"{price_val:,.2f}")
        else:
            st.warning("데이터를 불러올 수 없습니다. 올바른 티커인지 확인해주세요.")
            
    except Exception as e:
        st.error(f"시스템 오류 발생: {e}")
