import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="티커 자동완성기", layout="centered")

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
            {"name_kr": "애플", "ticker": "AAPL"},
            {"name_kr": "마이크로소프트", "ticker": "MSFT"}
        ]

stock_list = load_data()
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 상태 관리 ---

if 'ticker' not in st.session_state:
    st.session_state['ticker'] = ""
if 'search_mode' not in st.session_state:
    st.session_state['search_mode'] = True

# [동작 A] 검색창에서 선택 시 -> 티커만 추출하여 결과 모드로 전환
def on_select():
    selection = st.session_state.search_box
    if selection:
        # "엔비디아 (NVDA)" -> "NVDA" 추출
        ticker = selection.split('(')[-1].replace(')', '')
        st.session_state['ticker'] = ticker
        st.session_state['search_mode'] = False # 결과창 모드로 변경

# [동작 B] 결과창을 건드렸을 때 -> 다시 검색 모드로 복귀
def on_modify():
    st.session_state['search_mode'] = True
    st.session_state['ticker'] = ""

# --- UI 구현 (같은 자리에서 변신) ---

st.title("📈 티커 검색기")
st.caption("이름으로 검색하면 **티커**만 입력됩니다.")

# 위젯이 교체될 공간
ui_container = st.empty()

if st.session_state['search_mode']:
    # [모드 1] 검색창 (자동완성)
    with ui_container:
        st.selectbox(
            "종목 검색",
            options=search_options,
            index=None,
            placeholder="기업명을 입력하세요 (예: 삼성, 엔비...)",
            key="search_box",
            on_change=on_select,
            label_visibility="collapsed"
        )
else:
    # [모드 2] 결과창 (티커 텍스트만 남음)
    with ui_container:
        st.text_input(
            "티커",
            value=st.session_state['ticker'],
            key="result_box",
            on_change=on_modify, # 클릭해서 내용을 지우면 즉시 검색모드로
            label_visibility="collapsed"
        )

# --- 결과 및 차트 출력 (오류 수정됨) ---

final_ticker = st.session_state['ticker']

if final_ticker and not st.session_state['search_mode']:
    st.divider()
    try:
        # 데이터 다운로드
        df = yf.download(final_ticker, period="1mo", progress=False)
        
        if not df.empty:
            st.subheader(f"📊 {final_ticker} 차트")
            st.line_chart(df['Close'])
            
            # [오류 해결 핵심] Series 객체를 float(실수)로 명확하게 변환
            last_close_series = df['Close'].iloc[-1]
            
            # yfinance 버전에 따라 스칼라가 아닌 Series가 반환될 수 있으므로 처리
            try:
                current_price = float(last_close_series.item())
            except:
                current_price = float(last_close_series)

            st.metric("최근 종가", f"{current_price:,.2f}")
        else:
            st.error("데이터를 찾을 수 없습니다.")
            
    except Exception as e:
        # 디버깅을 위해 에러 메시지는 숨기고 사용자에게 안내
        st.error(f"데이터를 불러오는 중 문제가 발생했습니다. (티커 확인 필요)")
