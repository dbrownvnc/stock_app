import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="스마트 티커 검색", page_icon="📈")

# 2. 데이터 로드 (stocks.json 활용)
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

# 'edit_mode'가 True면 검색창이 뜨고, False면 결과값(티커)이 고정됨
if 'edit_mode' not in st.session_state:
    st.session_state['edit_mode'] = True
if 'selected_ticker' not in st.session_state:
    st.session_state['selected_ticker'] = ""

# [이벤트 1] 검색창에서 종목을 선택했을 때
def on_select():
    val = st.session_state.search_box
    if val:
        # 티커 추출 및 저장
        ticker = val.split('(')[-1].replace(')', '')
        st.session_state['selected_ticker'] = ticker
        # 선택 완료되었으므로 편집 모드 종료
        st.session_state['edit_mode'] = False

# [이벤트 2] 입력된 티커를 클릭(선택)하여 다시 입력하고 싶을 때
def enable_edit():
    st.session_state['edit_mode'] = True
    st.session_state['selected_ticker'] = ""

# --- UI 구현 ---

st.title("🔍 주식 티커 통합 검색")

# 같은 자리에 위젯을 교체하기 위한 컨테이너
container = st.empty()

if st.session_state['edit_mode']:
    # [상태 1] 검색 모드 (사용자가 텍스트 입력 중)
    with container:
        st.selectbox(
            "기업 검색",
            options=search_options,
            index=None,
            placeholder="기업명을 입력하세요...",
            key="search_box",
            on_change=on_select,
            label_visibility="collapsed"
        )
else:
    # [상태 2] 완성 모드 (티커가 입력창에 남아있는 모습)
    with container:
        # 이 입력창을 클릭하거나 내용을 바꾸려고 하면 즉시 enable_edit 함수 실행
        st.text_input(
            "티커",
            value=st.session_state['selected_ticker'],
            key="display_box",
            on_change=enable_edit, # 사용자가 글자를 지우거나 수정하려 하면 즉시 검색모드로!
            label_visibility="collapsed",
            help="클릭 후 내용을 지우면 다시 검색할 수 있습니다."
        )

# --- 차트 및 데이터 출력 ---
current_ticker = st.session_state['selected_ticker']

if current_ticker:
    st.divider()
    st.subheader(f"📊 {current_ticker} 분석")
    
    # 여기서 바로 차트를 보여주거나 버튼을 배치할 수 있습니다.
    if st.button(f"{current_ticker} 데이터 불러오기"):
        with st.spinner("로딩 중..."):
            df = yf.download(current_ticker, period="1mo", progress=False)
            if not df.empty:
                st.line_chart(df['Close'])
            else:
                st.error("데이터를 찾을 수 없습니다.")
