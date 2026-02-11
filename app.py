import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="주식 티커 자동완성", page_icon="⚡")

# 2. 데이터 로드 (캐싱)
@st.cache_data
def load_stock_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

stock_list = load_stock_data()

# 검색용 리스트 만들기 ["삼성전자 (005930.KS)", "엔비디아 (NVDA)", ...]
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 핵심 로직: 상태(State) 관리 ---

# 'selected_ticker' 변수가 없으면 초기화 (현재 선택된 티커)
if 'current_ticker' not in st.session_state:
    st.session_state['current_ticker'] = None

# 검색창에서 선택했을 때 실행될 콜백 함수
def on_select():
    # 선택된 값 가져오기 (예: "엔비디아 (NVDA)")
    choice = st.session_state.search_box
    if choice:
        # 괄호 안의 티커만 추출 ("NVDA")
        ticker = choice.split('(')[-1].replace(')', '')
        st.session_state['current_ticker'] = ticker

# 입력창에서 텍스트를 지웠을 때 실행될 콜백 함수 (다시 검색 모드로)
def on_clear():
    # 입력창이 비워지면 상태를 None으로 변경하여 다시 검색창을 띄움
    if not st.session_state.ticker_input:
        st.session_state['current_ticker'] = None

# --- UI 구현 (같은 자리에 위젯 교체하기) ---

st.title("⚡ 주식 티커 통합 검색기")
st.markdown("검색어를 입력하고 선택하면 **티커**로 변환됩니다.")

# ★ 마법의 자리 표시자 (이 위치에 위젯이 번갈아 나타남)
input_container = st.empty()

# [상태 1] 티커가 선택되지 않았을 때 -> "검색창(Selectbox)" 표시
if st.session_state['current_ticker'] is None:
    with input_container:
        st.selectbox(
            "종목 검색",
            options=search_options,
            index=None,
            placeholder="기업명을 입력하세요 (예: 엔비, 삼성...)",
            key="search_box",
            on_change=on_select, # 선택하면 즉시 변환 함수 실행
            label_visibility="collapsed" # 라벨 숨김 (깔끔하게)
        )
        st.info("👆 위 박스에 기업명을 입력해보세요.")

# [상태 2] 티커가 선택되었을 때 -> "입력창(Text Input)" 표시
else:
    with input_container:
        # 사용자가 수정을 원할 수 있으므로 text_input으로 보여줌
        # 값은 "NVDA" 처럼 티커만 들어감
        st.text_input(
            "티커",
            value=st.session_state['current_ticker'],
            key="ticker_input",
            on_change=on_clear, # 내용을 지우면 다시 검색창으로 돌아감
            label_visibility="collapsed"
        )
        st.caption("✅ 티커가 입력되었습니다. (지우면 다시 검색)")

# --- 결과 출력 (티커가 있을 때만 실행) ---
final_ticker = st.session_state['current_ticker']

if final_ticker:
    st.divider()
    if st.button(f"'{final_ticker}' 차트 보기", type="primary"):
        with st.spinner('데이터 불러오는 중...'):
            try:
                df = yf.download(final_ticker, period="1mo", progress=False)
                if not df.empty:
                    st.line_chart(df['Close'])
                    current_price = df['Close'].iloc[-1]
                    try: 
                        val = current_price.item()
                    except: 
                        val = current_price
                    st.metric("현재 주가", f"{val:,.2f}")
                else:
                    st.error("데이터를 찾을 수 없습니다.")
            except Exception as e:
                st.error(f"오류: {e}")
