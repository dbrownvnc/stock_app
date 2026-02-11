import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="원터치 티커 검색", page_icon="⚡")

# 2. 데이터 준비
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
            {"name_kr": "애플", "ticker": "AAPL"},
        ]

stock_list = load_data()
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 핵심 로직: 상태 관리 ---

# 현재 선택된 티커가 있는지 확인
if 'selected_ticker' not in st.session_state:
    st.session_state['selected_ticker'] = None

# [A] 검색창에서 선택 시 실행 -> 티커 저장
def on_select():
    selection = st.session_state.search_box
    if selection:
        ticker = selection.split('(')[-1].replace(')', '')
        st.session_state['selected_ticker'] = ticker

# [B] 결과 버튼 클릭 시 실행 -> 초기화 (다시 검색 모드)
def on_reset():
    st.session_state['selected_ticker'] = None


# --- UI 구현 ---

st.title("⚡ 원터치 티커 검색기")
st.write("결과를 클릭하면 다시 검색할 수 있습니다.")

# 위젯이 들어갈 자리 (컨테이너)
input_container = st.empty()

# [상태 1] 티커가 없을 때 -> 검색창(Selectbox) 표시
if st.session_state['selected_ticker'] is None:
    with input_container:
        st.selectbox(
            "종목 검색",
            options=search_options,
            index=None,
            placeholder="기업명을 입력하세요 (예: 엔비, 삼성...)",
            key="search_box",
            on_change=on_select, # 선택 즉시 상태 변경
            label_visibility="collapsed"
        )

# [상태 2] 티커가 있을 때 -> [버튼]으로 표시 (클릭하면 리셋됨)
else:
    with input_container:
        # 버튼의 라벨을 티커로 설정
        # use_container_width=True를 써서 입력창처럼 꽉 차게 보이게 함
        st.button(
            label=st.session_state['selected_ticker'],  # 버튼 글씨 = "NVDA"
            key="reset_btn",
            on_click=on_reset,  # 클릭하면 초기화 함수 실행
            use_container_width=True, # 화면 너비 꽉 채우기
            type="primary", # 강조 색상 (선택됨을 표현)
            help="클릭하면 다시 검색할 수 있습니다."
        )
        st.caption("👆 위 티커를 클릭하면 다시 검색합니다.")

# --- 결과 차트 출력 ---
current_ticker = st.session_state['selected_ticker']

if current_ticker:
    st.divider()
    with st.spinner(f"'{current_ticker}' 데이터 불러오는 중..."):
        try:
            df = yf.download(current_ticker, period="1mo", progress=False)
            if not df.empty:
                st.line_chart(df['Close'])
            else:
                st.warning("데이터가 없습니다.")
        except:
            pass
