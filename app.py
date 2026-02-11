import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="주식 티커 자동완성", page_icon="⚡")

# 2. 데이터 준비
@st.cache_data
def load_data():
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
        ]
    return stock_list

stock_list = load_data()

# 3. 검색 데이터 생성
# 검색창 옵션: "엔비디아 (NVDA)"
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 상태 관리 ---

if 'selected_ticker' not in st.session_state:
    st.session_state['selected_ticker'] = None

# [기능 1] 검색창에서 선택 시 -> 티커 확정
def on_select():
    selection = st.session_state.search_box
    if selection:
        ticker = selection.split('(')[-1].replace(')', '')
        st.session_state['selected_ticker'] = ticker

# [기능 2] 결과 버튼 클릭 시 -> 검색 모드로 복귀 (초기화)
def on_reset():
    st.session_state['selected_ticker'] = None

# --- UI 구현 ---

st.title("⚡ 원터치 티커 검색기")
st.write("완성된 티커를 **클릭**하면 다시 검색할 수 있습니다.")

# 위젯 자리 표시자
placeholder = st.empty()

# [상태 A] 검색 모드 (아직 선택 안 함)
if st.session_state['selected_ticker'] is None:
    with placeholder:
        st.selectbox(
            label="종목 검색",
            options=search_options,
            index=None,
            placeholder="기업명을 입력하세요...",
            key="search_box",
            on_change=on_select,
            label_visibility="collapsed"
        )

# [상태 B] 결과 모드 (티커 확정됨)
else:
    ticker = st.session_state['selected_ticker']
    with placeholder:
        # ★ 핵심 포인트: 결과를 '버튼'으로 보여줍니다.
        # 버튼을 누르면 on_reset 함수가 실행되어 다시 검색창이 뜹니다.
        st.button(
            label=f"✅ {ticker}  (클릭하여 수정)", # 버튼에 표시될 텍스트
            on_click=on_reset,                    # 클릭 시 초기화 실행
            use_container_width=True,             # 입력창처럼 꽉 차게 보임
            type="primary"                        # 강조 색상 (선택사항)
        )

# --- 차트 출력 ---
current_ticker = st.session_state['selected_ticker']

if current_ticker:
    st.divider()
    if st.button("차트 조회"):
        with st.spinner(f"{current_ticker} 데이터 불러오는 중..."):
            try:
                df = yf.download(current_ticker, period="1mo", progress=False)
                if not df.empty:
                    st.line_chart(df['Close'])
                else:
                    st.error("데이터가 없습니다.")
            except Exception as e:
                st.error("오류 발생")
