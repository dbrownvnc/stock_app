import streamlit as st
import json
import yfinance as yf

# 1. 데이터 로드 (캐싱)
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

# --- 핵심 로직: 상태 관리 ---

if 'ticker' not in st.session_state:
    st.session_state['ticker'] = ""
if 'search_mode' not in st.session_state:
    st.session_state['search_mode'] = True

def on_select():
    # 리스트에서 선택 시 실행
    val = st.session_state.search_box
    if val:
        ticker = val.split('(')[-1].replace(')', '')
        st.session_state['ticker'] = ticker
        st.session_state['search_mode'] = False  # 결과 모드로 전환

def on_re_edit():
    # 입력창 내용을 수정하거나 지울 때 실행
    st.session_state['search_mode'] = True
    st.session_state['ticker'] = ""

# --- UI 구현 ---

st.title("🔍 통합 티커 자동완성")

# 위젯이 교체될 컨테이너
ui_container = st.empty()

if st.session_state['search_mode']:
    # [모드 1] 자동완성 검색창
    with ui_container:
        st.selectbox(
            "Search",
            options=search_options,
            index=None,
            placeholder="기업명 입력 시 자동완성...",
            key="search_box",
            on_change=on_select,
            label_visibility="collapsed"
        )
else:
    # [모드 2] 결과 입력창 (티커가 텍스트로 남아있음)
    with ui_container:
        st.text_input(
            "Ticker",
            value=st.session_state['ticker'],
            key="display_input",
            on_change=on_re_edit,  # 내용을 건드리면 즉시 검색모드로 복귀
            label_visibility="collapsed"
        )

# --- 결과 출력 ---
final_ticker = st.session_state['ticker']

if final_ticker and not st.session_state['search_mode']:
    st.divider()
    try:
        df = yf.download(final_ticker, period="1mo", progress=False)
        if not df.empty:
            st.subheader(f"📊 {final_ticker} 주가 분석")
            st.line_chart(df['Close'])
        else:
            st.error("데이터를 찾을 수 없습니다.")
    except Exception as e:
        st.error(f"오류 발생: {e}")

st.caption("💡 완성된 티커를 클릭하고 지우면 언제든지 다시 자동완성 검색이 활성화됩니다.")
