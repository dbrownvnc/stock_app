import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="주식 티커 자동 변환기", layout="wide")

# 2. 데이터 로드 (캐싱 적용)
@st.cache_data
def load_stock_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

stock_list = load_stock_data()

# 3. 검색 데이터 준비
# (화면에 보여줄 이름) -> (실제 티커)를 찾는 딕셔너리 생성
search_dict = {}
search_options = []

for stock in stock_list:
    # 예: "삼성전자 (005930.KS)"
    display_name = f"{stock['name_kr']} ({stock['ticker']})"
    search_options.append(display_name)
    search_dict[display_name] = stock['ticker']

# --- 핵심 로직: 세션 상태 관리 ---

# A. 티커를 저장할 변수 초기화 (없으면 빈 문자열)
if 'target_ticker' not in st.session_state:
    st.session_state['target_ticker'] = ""

# B. 콜백 함수: 검색창에서 선택했을 때 실행되는 함수
def on_stock_select():
    # 검색창(selectbox)의 현재 선택된 값을 가져옴
    selected_text = st.session_state['stock_selector']
    
    if selected_text:
        # 딕셔너리에서 티커를 찾아 'target_ticker' 변수에 덮어씀
        ticker = search_dict[selected_text]
        st.session_state['target_ticker'] = ticker

# --- UI 구성 ---

st.title("⚡ 주식 티커 자동 변환기")
st.markdown("기업명을 선택하면 **티커 코드로 자동 변환**되어 입력됩니다.")

col1, col2 = st.columns([1, 1])

with col1:
    # [검색창]
    # on_change=on_stock_select : 값이 바뀌면 위에서 만든 함수가 실행됨
    st.selectbox(
        "기업명 검색 (한글/영어)",
        options=search_options,
        index=None,
        placeholder="검색어를 입력하세요...",
        key="stock_selector", 
        on_change=on_stock_select 
    )

with col2:
    # [입력창]
    # value=st.session_state['target_ticker'] : 세션에 저장된 티커 값이 여기에 표시됨
    final_ticker = st.text_input(
        "티커 (자동 입력됨)",
        value=st.session_state['target_ticker'],
        key="ticker_input" 
    )

st.divider()

# --- 결과 처리 ---
if final_ticker:
    st.subheader(f"📈 {final_ticker} 차트")
    
    if st.button("차트 보기"):
        with st.spinner('데이터 로딩 중...'):
            try:
                df = yf.download(final_ticker, period="1mo", progress=False)
                if not df.empty:
                    st.line_chart(df['Close'])
                    st.success(f"'{final_ticker}' 데이터 로드 성공")
                else:
                    st.error("데이터가 없습니다.")
            except Exception as e:
                st.error(f"오류: {e}")
