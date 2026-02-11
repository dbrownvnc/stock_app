import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="무한 자동완성 검색기", page_icon="🔄")

# 2. 데이터 로드
@st.cache_data
def load_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return [
            {"name_kr": "삼성전자", "ticker": "005930.KS"},
            {"name_kr": "엔비디아", "ticker": "NVDA"},
            {"name_kr": "테슬라", "ticker": "TSLA"},
            {"name_kr": "애플", "ticker": "AAPL"}
        ]

stock_list = load_data()
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 핵심: 세션 상태 관리 (무한 루프의 핵심) ---

# 초기 상태 설정
if 'selected_ticker' not in st.session_state:
    st.session_state['selected_ticker'] = ""
if 'input_mode' not in st.session_state:
    st.session_state['input_mode'] = "search"  # "search" 또는 "result"

# [함수 1] 검색창에서 종목을 선택했을 때 실행
def handle_selection():
    if st.session_state.search_box:
        # 선택된 값에서 티커만 추출
        ticker = st.session_state.search_box.split('(')[-1].replace(')', '')
        st.session_state['selected_ticker'] = ticker
        st.session_state['input_mode'] = "result"
        # 검색창 자체는 비워줌 (다음에 돌아왔을 때를 위해)
        st.session_state.search_box = None

# [함수 2] 티커 결과창을 클릭하여 수정하려 할 때 실행
def handle_re_edit():
    # 사용자가 결과창의 텍스트를 건드리면(지우거나 수정하면) 즉시 검색 모드로 복구
    st.session_state['input_mode'] = "search"
    st.session_state['selected_ticker'] = ""

# --- UI 구현 ---

st.title("🔄 무한 자동완성 티커 검색")
st.write("선택하면 티커로 변환되고, 티커를 지우면 다시 검색창이 뜹니다.")

# 동일한 위치에 위젯을 교체하기 위한 placeholder
placeholder = st.empty()

if st.session_state['input_mode'] == "search":
    # [상태 1] 검색 모드
    with placeholder:
        st.selectbox(
            "종목 검색",
            options=search_options,
            index=None,
            placeholder="기업명을 입력하세요...",
            key="search_box",
            on_change=handle_selection,
            label_visibility="collapsed"
        )
else:
    # [상태 2] 티커 결과 모드
    with placeholder:
        # 사용자가 이 창을 클릭하고 글자를 지우는 순간 handle_re_edit 실행됨
        st.text_input(
            "확정된 티커",
            value=st.session_state['selected_ticker'],
            key="result_box",
            on_change=handle_re_edit,
            label_visibility="collapsed"
        )

# --- 결과 출력 (티커가 확정되었을 때만) ---
if st.session_state['selected_ticker'] and st.session_state['input_mode'] == "result":
    ticker = st.session_state['selected_ticker']
    st.success(f"현재 입력된 티커: **{ticker}**")
    
    # 차트 기능 예시
    if st.button(f"{ticker} 차트 불러오기"):
        with st.spinner("데이터 수신 중..."):
            df = yf.download(ticker, period="1mo", progress=False)
            if not df.empty:
                st.line_chart(df['Close'])
            else:
                st.error("데이터를 찾을 수 없습니다.")

st.divider()
st.caption("💡 팁: 자동완성된 티커를 클릭하고 'Backspace'로 지우면 바로 다시 검색할 수 있습니다.")
