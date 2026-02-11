import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="Stock Ticker Search", layout="centered")

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
# 검색 시 보여줄 리스트: "삼성전자 (005930.KS)"
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 핵심 상태 관리 로직 ---

if 'ticker' not in st.session_state:
    st.session_state['ticker'] = ""
if 'show_search' not in st.session_state:
    st.session_state['show_search'] = True

# [A] 자동완성 리스트에서 종목을 선택했을 때 실행
def on_select():
    val = st.session_state.search_box
    if val:
        # 티커만 추출하여 저장
        ticker_only = val.split('(')[-1].replace(')', '')
        st.session_state['ticker'] = ticker_only
        st.session_state['show_search'] = False # 입력창(티커만 보임) 모드로 전환

# [B] 티커만 남은 입력창을 클릭/수정할 때 실행
def on_re_edit():
    # 사용자가 입력을 시도하면 다시 검색(자동완성) 모드로 전환
    st.session_state['show_search'] = True
    st.session_state['ticker'] = ""

# --- UI 구현 (단일 창 UI) ---

st.title("🔍 Stock Ticker Search")

# 위젯이 들어갈 고정 자리
input_ui = st.empty()

if st.session_state['show_search']:
    # [모드 1] 자동완성 검색창 (이름+티커 다 보임)
    with input_ui:
        st.selectbox(
            label="Search",
            options=search_options,
            index=None,
            placeholder="기업명 또는 티커 입력...",
            key="search_box",
            on_change=on_select,
            label_visibility="collapsed"
        )
else:
    # [모드 2] 결과 입력창 (오직 티커만 남음)
    with input_ui:
        st.text_input(
            label="Ticker",
            value=st.session_state['ticker'],
            key="ticker_input",
            on_change=on_re_edit, # 클릭 후 수정 시 즉시 자동완성 모드로 복귀
            label_visibility="collapsed"
        )

# --- 하단 결과 분석 (차트 등) ---
final_ticker = st.session_state['ticker']

if final_ticker and not st.session_state['show_search']:
    try:
        df = yf.download(final_ticker, period="1mo", progress=False)
        if not df.empty:
            st.subheader(f"📊 {final_ticker} Chart")
            st.line_chart(df['Close'])
        else:
            st.error("데이터를 찾을 수 없는 티커입니다.")
    except Exception as e:
        st.error("오류가 발생했습니다.")

st.caption("💡 완성된 티커를 클릭하고 지우면 언제든지 다시 검색할 수 있습니다.")
