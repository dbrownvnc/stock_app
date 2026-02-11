import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="통합 자동완성 검색기", page_icon="🔍")

# 2. 데이터 로드 (stocks.json 활용)
@st.cache_data
def load_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # 데이터 파일이 없을 경우를 대비한 기본 리스트
        return [
            {"name_kr": "삼성전자", "ticker": "005930.KS"},
            {"name_kr": "SK하이닉스", "ticker": "000660.KS"},
            {"name_kr": "엔비디아", "ticker": "NVDA"},
            {"name_kr": "테슬라", "ticker": "TSLA"},
            {"name_kr": "애플", "ticker": "AAPL"},
            {"name_kr": "마이크로소프트", "ticker": "MSFT"}
        ]

stock_list = load_data()
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 핵심 로직: 무한 반복 상태 관리 ---

# 'is_confirmed'가 True면 결과 티커 표시, False면 자동완성 검색창 표시
if 'is_confirmed' not in st.session_state:
    st.session_state['is_confirmed'] = False
if 'current_ticker' not in st.session_state:
    st.session_state['current_ticker'] = ""

# [동작 1] 자동완성 리스트에서 종목을 선택했을 때
def on_selection():
    if st.session_state.search_input:
        # "엔비디아 (NVDA)" -> "NVDA"만 추출
        ticker = st.session_state.search_input.split('(')[-1].replace(')', '')
        st.session_state['current_ticker'] = ticker
        st.session_state['is_confirmed'] = True
        # 다음 검색을 위해 검색 위젯의 내부 값은 리셋
        st.session_state.search_input = None

# [동작 2] 결과창(티커)을 클릭하거나 수정하려고 할 때
def on_edit():
    # 사용자가 글자를 지우거나 고치면 즉시 검색 모드로 복귀
    st.session_state['is_confirmed'] = False
    # 기존 티커를 지워줌으로써 검색창이 빈 상태로 뜨게 함
    st.session_state['current_ticker'] = ""

# --- UI 구현 (입력창 위치 고정) ---

st.title("📈 주식 티커 검색")
st.write("기업명을 입력해 티커를 완성하세요. 완성 후 클릭하면 재입력이 가능합니다.")

# 입력창이 들어갈 공간 확보
input_container = st.empty()

if not st.session_state['is_confirmed']:
    # [모드 A] 자동완성 검색 모드
    with input_container:
        st.selectbox(
            "기업 검색",
            options=search_options,
            index=None,
            placeholder="기업명을 입력하세요 (예: 삼성, 엔비...)",
            key="search_input",
            on_change=on_selection,
            label_visibility="collapsed"
        )
else:
    # [모드 B] 결과 고정 모드 (입력창에 티커가 남겨진 상태)
    with input_container:
        st.text_input(
            "티커 결과",
            value=st.session_state['current_ticker'],
            key="result_display",
            on_change=on_edit, # 사용자가 여기서 내용을 수정/삭제하면 즉시 검색모드로 전환
            label_visibility="collapsed"
        )

# --- 하단 결과 출력부 ---
current_val = st.session_state['current_ticker']

if current_val and st.session_state['is_confirmed']:
    st.divider()
    st.success(f"현재 선택된 티커: **{current_val}**")
    
    # 예시: 주가 데이터 불러오기 버튼
    if st.button(f"{current_val} 차트 보기"):
        with st.spinner("데이터 로드 중..."):
            try:
                df = yf.download(current_val, period="1mo", progress=False)
                if not df.empty:
                    st.line_chart(df['Close'])
                else:
                    st.error("데이터를 불러올 수 없습니다.")
            except:
                st.error("티커를 확인해주세요.")

st.caption("💡 완성된 티커를 클릭하고 지우면 다시 처음처럼 검색할 수 있습니다.")
