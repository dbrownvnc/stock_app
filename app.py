import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="Ticker Search", layout="centered")

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

# --- 상태 관리 로직 ---

if 'ticker' not in st.session_state:
    st.session_state['ticker'] = ""
if 'edit_mode' not in st.session_state:
    st.session_state['edit_mode'] = True

# [A] 검색창에서 종목을 골랐을 때
def on_select():
    val = st.session_state.search_box
    if val:
        ticker = val.split('(')[-1].replace(')', '')
        st.session_state['ticker'] = ticker
        st.session_state['edit_mode'] = False # 결과 고정 모드로 변경

# [B] 완성된 티커창을 클릭/수정할 때
def on_re_edit():
    st.session_state['edit_mode'] = True # 다시 검색 모드로 변경
    st.session_state['ticker'] = ""

# --- UI 구현 (입력창 하나만 노출) ---

st.title("📈 Stock Analyzer")

# 입력창이 놓일 단일 위치
ui_space = st.empty()

if st.session_state['edit_mode']:
    # [모드 1] 검색/자동완성 창
    with ui_space:
        st.selectbox(
            label="Search",
            options=search_options,
            index=None,
            placeholder="기업명 또는 티커를 입력하세요",
            key="search_box",
            on_change=on_select,
            label_visibility="collapsed"
        )
else:
    # [모드 2] 결과 티커 창 (자동완성된 결과가 입력창에 남음)
    with ui_space:
        st.text_input(
            label="Ticker",
            value=st.session_state['ticker'],
            key="result_box",
            on_change=on_re_edit, # 클릭 후 수정/삭제 시 즉시 검색모드로 전환
            label_visibility="collapsed"
        )

# --- 결과 로직 (입력창 바로 아래에 차트 출력) ---
final_ticker = st.session_state['ticker']

if final_ticker and not st.session_state['edit_mode']:
    # 별도의 "선택된 티커: XX" 같은 텍스트 없이 바로 기능을 수행합니다.
    try:
        # 데이터가 있는지 확인 후 차트 출력
        df = yf.download(final_ticker, period="1mo", progress=False)
        if not df.empty:
            st.line_chart(df['Close'])
        else:
            st.error("데이터를 불러올 수 없는 티커입니다.")
    except Exception as e:
        st.error("오류가 발생했습니다.")
