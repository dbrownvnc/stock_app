import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="티커 자동완성", page_icon="⚡")

# 2. 데이터 준비
@st.cache_data
def load_data():
    # 파일이 없을 경우를 대비한 샘플 데이터
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
            {"name_kr": "마이크로소프트", "ticker": "MSFT"},
        ]
    return stock_list

stock_list = load_data()

# 3. 검색용 옵션 리스트 생성
# 예: "삼성전자 (005930.KS)"
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 핵심 로직: 상태(State) 관리 ---

# 현재 모드 설정 (True: 티커 확정 상태 / False: 검색 중 상태)
if 'is_confirmed' not in st.session_state:
    st.session_state['is_confirmed'] = False
if 'current_value' not in st.session_state:
    st.session_state['current_value'] = ""

# [이벤트 1] 검색창에서 선택했을 때 -> 티커 확정 모드로 변경
def on_search():
    selection = st.session_state.search_input
    if selection:
        # "엔비디아 (NVDA)" -> "NVDA" 추출
        ticker = selection.split('(')[-1].replace(')', '')
        st.session_state['current_value'] = ticker
        st.session_state['is_confirmed'] = True

# [이벤트 2] 확정된 티커 입력창을 건드렸을 때
def on_result_change():
    # 현재 입력된 값을 가져옴
    new_val = st.session_state.result_input
    
    # 만약 내용을 지웠다면? -> 다시 검색 모드로 복귀
    if not new_val:
        st.session_state['is_confirmed'] = False
        st.session_state['current_value'] = ""
    # 내용을 지운 게 아니라 수정한 거라면? (예: NVDA -> NV) -> 값만 업데이트
    else:
        st.session_state['current_value'] = new_val

# [이벤트 3] 강제 리셋 (X 버튼)
def reset_search():
    st.session_state['is_confirmed'] = False
    st.session_state['current_value'] = ""

# --- UI 구현 (같은 자리에서 변신) ---

st.title("⚡ 티커 자동 변환기")
st.markdown("기업명을 선택하면 티커로 변환됩니다.")

# 위젯이 그려질 자리 (이 자리에 검색창 또는 결과창이 번갈아 뜸)
input_spot = st.empty()

# [상황 A] 아직 선택 안함 -> 검색창(Selectbox) 보여주기
if not st.session_state['is_confirmed']:
    with input_spot:
        st.selectbox(
            label="종목 검색",
            options=search_options,
            index=None,
            placeholder="기업명을 입력하세요 (예: 엔비, 삼성...)",
            key="search_input",
            on_change=on_search, # 선택 즉시 실행
            label_visibility="collapsed"
        )

# [상황 B] 선택 완료 -> 결과창(Text Input) 보여주기 (값은 티커)
else:
    with input_spot:
        col_in, col_btn = st.columns([8, 1])
        
        with col_in:
            st.text_input(
                label="티커",
                value=st.session_state['current_value'],
                key="result_input",
                on_change=on_result_change, # 수정 시 실행
                label_visibility="collapsed"
            )
        
        with col_btn:
            # 재입력을 쉽게 하기 위한 초기화 버튼
            st.button("🔄", on_click=reset_search, help="다시 검색하기")

# --- 하단 결과 로직 ---
final_ticker = st.session_state['current_value'] if st.session_state['is_confirmed'] else None

if final_ticker:
    st.caption("✅ 티커 입력 완료! (수정하려면 위 텍스트를 지우거나 🔄 버튼 클릭)")
    st.divider()
    
    # 실제 데이터 조회 예시
    if st.button("차트 조회"):
        with st.spinner(f"'{final_ticker}' 데이터 조회 중..."):
            try:
                df = yf.download(final_ticker, period="1mo", progress=False)
                if not df.empty:
                    st.line_chart(df['Close'])
                else:
                    st.error("데이터가 없습니다.")
            except:
                st.error("올바르지 않은 티커입니다.")
