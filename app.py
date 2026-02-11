import streamlit as st
import json

# 1. 페이지 설정
st.set_page_config(page_title="주식 티커 검색", page_icon="🔍")

# 2. 데이터 준비 (테스트용 데이터 포함)
@st.cache_data
def load_data():
    # 실제로는 stocks.json 파일을 읽어야 하지만, 
    # 파일이 없을 경우를 대비해 기본 데이터를 넣어둡니다.
    default_data = [
        {"name_kr": "삼성전자", "ticker": "005930.KS"},
        {"name_kr": "SK하이닉스", "ticker": "000660.KS"},
        {"name_kr": "엔비디아", "ticker": "NVDA"},
        {"name_kr": "테슬라", "ticker": "TSLA"},
        {"name_kr": "애플", "ticker": "AAPL"},
        {"name_kr": "마이크로소프트", "ticker": "MSFT"},
        {"name_kr": "구글(알파벳)", "ticker": "GOOGL"},
        {"name_kr": "아마존", "ticker": "AMZN"},
        {"name_kr": "넷플릭스", "ticker": "NFLX"},
        {"name_kr": "카카오", "ticker": "035720.KS"},
        {"name_kr": "네이버", "ticker": "035420.KS"},
    ]
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default_data

stock_list = load_data()

# 3. 검색용 옵션 만들기
# 예: "엔비디아 (NVDA)"
option_map = {f"{s['name_kr']} ({s['ticker']})": s['ticker'] for s in stock_list}
search_options = list(option_map.keys())

# --- 핵심 로직: 세션 상태 관리 ---

# 'selected_ticker'가 없으면 초기화
if 'selected_ticker' not in st.session_state:
    st.session_state['selected_ticker'] = None

# [기능 1] 검색창에서 선택했을 때 실행
def on_search_change():
    selection = st.session_state.search_box_key
    if selection:
        # 선택된 값에서 티커만 추출하여 상태 저장
        ticker = option_map[selection]
        st.session_state['selected_ticker'] = ticker

# [기능 2] 입력창에서 내용을 지웠을 때 실행 (다시 검색모드로)
def on_input_change():
    # 입력된 텍스트가 없으면 검색 모드로 초기화
    if not st.session_state.input_box_key:
        st.session_state['selected_ticker'] = None


# --- UI 그리기 ---

st.title("🔍 주식 티커 검색기")
st.write("기업명을 선택하면 티커로 변환됩니다.")

# 1. 티커가 선택되지 않은 상태 -> [검색창(Selectbox)] 보여줌
if st.session_state['selected_ticker'] is None:
    st.selectbox(
        label="기업명 검색",
        options=search_options,
        index=None,
        placeholder="기업명을 선택하세요...",
        key="search_box_key",
        on_change=on_search_change,  # 값이 바뀌면 즉시 실행
    )

# 2. 티커가 선택된 상태 -> [텍스트 입력창(Text Input)] 보여줌
else:
    # 컬럼을 나눠서 '입력창'과 '취소버튼'을 배치
    col1, col2 = st.columns([8, 1])
    
    with col1:
        st.text_input(
            label="티커 코드",
            value=st.session_state['selected_ticker'],
            key="input_box_key",
            on_change=on_input_change
        )
    
    with col2:
        # X 버튼을 누르면 강제로 검색 모드로 복귀
        if st.button("❌", help="다시 검색하기"):
            st.session_state['selected_ticker'] = None
            st.rerun() # 화면 즉시 새로고침

# --- 결과 확인용 (티커가 있을 때만 표시) ---
if st.session_state['selected_ticker']:
    ticker = st.session_state['selected_ticker']
    st.success(f"입력된 티커: **{ticker}**")
    
    # 여기에 yfinance 차트 코드 등을 넣으면 됩니다.
    # import yfinance as yf
    # st.line_chart(yf.download(ticker, period='1mo')['Close'])
