import streamlit as st
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="주식 티커 자동완성", page_icon="⚡")

# 2. 데이터 준비 (테스트용 데이터)
# 실제로는 stocks.json 파일을 로드해서 쓰시면 됩니다.
@st.cache_data
def get_stock_data():
    return [
        {"name": "삼성전자", "ticker": "005930.KS"},
        {"name": "SK하이닉스", "ticker": "000660.KS"},
        {"name": "엔비디아 (NVIDIA)", "ticker": "NVDA"},
        {"name": "테슬라 (Tesla)", "ticker": "TSLA"},
        {"name": "애플 (Apple)", "ticker": "AAPL"},
        {"name": "마이크로소프트 (MSFT)", "ticker": "MSFT"},
        {"name": "아마존 (Amazon)", "ticker": "AMZN"},
        {"name": "구글 (Alphabet)", "ticker": "GOOGL"},
        {"name": "넷플릭스 (Netflix)", "ticker": "NFLX"},
        {"name": "카카오", "ticker": "035720.KS"},
        {"name": "네이버 (NAVER)", "ticker": "035420.KS"},
    ]

stocks = get_stock_data()

# 검색용 리스트 생성: ["삼성전자 | 005930.KS", "엔비디아 | NVDA", ...]
# 팁: 검색 편의를 위해 이름과 티커를 모두 포함시킵니다.
search_options = [f"{s['name']}  |  {s['ticker']}" for s in stocks]

# --- 핵심 로직: 세션 상태 관리 ---

# 'final_ticker' : 최종적으로 입력창에 남을 티커 값
if 'final_ticker' not in st.session_state:
    st.session_state['final_ticker'] = ""

# [동작 1] 검색창에서 선택 시 실행 -> 티커만 발라내서 저장하고 화면 새로고침
def on_select_change():
    selection = st.session_state.search_widget
    if selection:
        # "엔비디아 | NVDA" 에서 "NVDA" 부분만 추출
        ticker_part = selection.split('|')[-1].strip()
        st.session_state['final_ticker'] = ticker_part
        st.session_state.search_widget = None # 검색창 초기화

# [동작 2] 결과창에서 X버튼이나 지우기를 했을 때 -> 다시 검색 모드로
def on_reset():
    st.session_state['final_ticker'] = ""


# --- UI 렌더링 (하나의 창처럼 보이게 하기) ---

st.title("⚡ 주식 티커 자동 변환기")
st.markdown("입력창에 **'엔비'**를 입력하고 선택해보세요. **'NVDA'**로 변신합니다.")

# 빈 공간(Container)을 만들어 둡니다. 이 자리에 위젯이 번갈아 들어갑니다.
input_area = st.empty()

# [상황 A] 아직 선택된 티커가 없을 때 -> "검색창(Selectbox)" 보여주기
if not st.session_state['final_ticker']:
    with input_area:
        st.selectbox(
            "종목 검색",
            options=search_options,
            index=None,
            placeholder="기업명을 입력하세요...",
            key="search_widget",
            on_change=on_select_change, # 선택 즉시 동작
            label_visibility="collapsed"
        )

# [상황 B] 티커가 확정되었을 때 -> "입력창(Text Input)" 보여주기
else:
    with input_area:
        # 컬럼을 나누어 [티커 입력창] + [지우기 버튼] 배치
        c1, c2 = st.columns([8, 1])
        
        with c1:
            # 여기에는 오직 "NVDA" 같은 티커만 표시됩니다.
            st.text_input(
                "티커",
                value=st.session_state['final_ticker'],
                disabled=False, # 사용자가 직접 수정 가능하게 하려면 False
                label_visibility="collapsed"
            )
        
        with c2:
            # X 버튼을 누르면 다시 검색창으로 돌아감
            if st.button("🔄", help="다시 검색하기"):
                on_reset()
                st.rerun()

# --- 결과 활용 ---

ticker = st.session_state['final_ticker']

if ticker:
    st.info(f"선택된 종목 코드: **{ticker}**")
    
    # 바로 차트 그리기
    if st.button("차트 조회"):
        with st.spinner(f"{ticker} 데이터 불러오는 중..."):
            try:
                df = yf.download(ticker, period="1mo", progress=False)
                if not df.empty:
                    st.line_chart(df['Close'])
                else:
                    st.error("데이터가 없습니다.")
            except Exception as e:
                st.error(f"에러: {e}")
