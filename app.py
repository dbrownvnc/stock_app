import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="무한 자동완성 검색기", layout="centered")

# 2. 데이터 로드
@st.cache_data
def load_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return [
            {"name_kr": "삼성전자", "ticker": "005930.KS"},
            {"name_kr": "SK하이닉스", "ticker": "000660.KS"},
            {"name_kr": "엔비디아", "ticker": "NVDA"},
            {"name_kr": "테슬라", "ticker": "TSLA"},
            {"name_kr": "애플", "ticker": "AAPL"}
        ]

stock_list = load_data()
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 핵심 로직: 상태 고정 및 자동 리셋 ---

if 'ticker' not in st.session_state:
    st.session_state['ticker'] = ""

def on_selection():
    # 사용자가 리스트에서 종목을 선택했을 때
    if st.session_state.search_input:
        # 티커만 추출하여 저장
        selected_ticker = st.session_state.search_input.split('(')[-1].replace(')', '')
        st.session_state['ticker'] = selected_ticker
        
        # ★ 핵심: 선택 직후 'search_input' 위젯의 값을 None으로 밀어버림
        # 이렇게 하면 입력창은 항상 비어있거나 검색 가능한 상태를 유지합니다.
        st.session_state.search_input = None

# --- UI 구현 ---

st.title("🔍 실시간 티커 검색")

# 현재 선택된 티커가 있으면 Placeholder에 표시하여 "티커만 남은 효과"를 줌
current_ticker = st.session_state['ticker']
placeholder_msg = f"선택됨: {current_ticker}" if current_ticker else "기업명 또는 티커 입력..."

# 단 하나의 입력창 (언제 클릭해도 바로 자동완성 리스트가 뜸)
st.selectbox(
    label="주식 검색",
    options=search_options,
    index=None, 
    placeholder=placeholder_msg,
    key="search_input",
    on_change=on_selection,
    label_visibility="collapsed"
)

# --- 결과 출력 (입력창 바로 아래에 차트 배치) ---
if st.session_state['ticker']:
    target = st.session_state['ticker']
    
    st.divider()
    try:
        # 데이터 가져오기
        df = yf.download(target, period="1mo", progress=False)
        if not df.empty:
            st.subheader(f"📊 {target} 한 달 주가 흐름")
            st.line_chart(df['Close'])
            
            # 현재가 등 간단한 정보 표시
            last_price = df['Close'].iloc[-1]
            st.write(f"최근 종가: **{last_price:,.2f}**")
        else:
            st.error("데이터를 찾을 수 없습니다.")
    except Exception as e:
        st.error(f"오류 발생: {e}")

st.caption("💡 입력창을 클릭하면 언제든지 즉시 다시 검색할 수 있습니다.")
