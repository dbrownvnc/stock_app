import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="주식 티커 자동완성", page_icon="⚡")

# 2. 데이터 로드 (캐싱)
@st.cache_data
def load_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

stock_list = load_data()

# 3. 검색용 데이터 사전 만들기 (이름 -> 티커 매핑)
# 검색창에 보여질 "이름 (티커)" 문자열과 실제 "티커"를 연결합니다.
search_map = {}
search_options = []

for stock in stock_list:
    # 드롭다운에 표시될 글자: "엔비디아 (NVDA) - NASDAQ"
    display_label = f"{stock['name_kr']} ({stock['ticker']})"
    search_options.append(display_label)
    
    # 이 라벨을 선택하면 실제 티커(NVDA)를 찾을 수 있게 저장
    search_map[display_label] = stock['ticker']

# --- 기능 구현 (Session State 활용) ---

# 만약 세션에 티커 값이 없으면 초기화
if 'target_ticker' not in st.session_state:
    st.session_state['target_ticker'] = ""

# 콜백 함수: 검색창에서 무언가 선택했을 때 실행됨
def update_ticker_input():
    selection = st.session_state.search_box  # 검색창의 현재 값
    if selection:
        # 선택된 라벨(엔비디아...)로 티커(NVDA)를 찾아서 입력창 상태 업데이트
        found_ticker = search_map[selection]
        st.session_state['target_ticker'] = found_ticker

# --- UI 구성 ---

st.title("⚡ 주식 티커 자동 변환기")

col1, col2 = st.columns([2, 1])

with col1:
    # [A] 검색 도우미 (Selectbox)
    st.selectbox(
        label="기업명으로 검색하세요 (자동완성)",
        options=search_options,
        index=None,
        placeholder="예: 삼성, 엔비, 테슬라...",
        key="search_box",       # 이 위젯의 ID
        on_change=update_ticker_input  # 값이 바뀌면 위의 함수 실행!
    )

with col2:
    # [B] 실제 티커 입력창 (Text Input)
    # 검색창에서 선택하면 여기가 자동으로 'NVDA'로 바뀝니다.
    # 사용자가 직접 타이핑해서 수정할 수도 있습니다.
    final_ticker = st.text_input(
        label="티커 코드 (자동 입력)",
        value=st.session_state['target_ticker'],
        key="ticker_input_field"
    )

st.divider()

# --- 결과 출력 ---
if final_ticker:
    st.subheader(f"📊 {final_ticker} 분석 결과")
    
    if st.button("데이터 불러오기"):
        try:
            with st.spinner(f"{final_ticker} 데이터를 가져오는 중..."):
                df = yf.download(final_ticker, period="1mo")
                
                if not df.empty:
                    st.line_chart(df['Close'])
                    st.success(f"현재가: ${df['Close'].iloc[-1]:.2f} (또는 원)")
                else:
                    st.error("데이터를 찾을 수 없습니다. 티커를 확인해주세요.")
        except Exception as e:
            st.error(f"오류 발생: {e}")
