import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="주식 티커 검색", page_icon="⚡")

# 2. 데이터 준비 (테스트용 데이터 포함)
@st.cache_data
def load_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # 파일이 없을 경우를 대비한 기본 데이터
        return [
            {"name_kr": "삼성전자", "ticker": "005930.KS"},
            {"name_kr": "SK하이닉스", "ticker": "000660.KS"},
            {"name_kr": "엔비디아", "ticker": "NVDA"},
            {"name_kr": "테슬라", "ticker": "TSLA"},
            {"name_kr": "애플", "ticker": "AAPL"},
            {"name_kr": "마이크로소프트", "ticker": "MSFT"},
            {"name_kr": "구글(알파벳)", "ticker": "GOOGL"},
            {"name_kr": "아마존", "ticker": "AMZN"},
            {"name_kr": "카카오", "ticker": "035720.KS"},
            {"name_kr": "네이버", "ticker": "035420.KS"},
        ]

stock_list = load_data()

# 3. 검색용 데이터 만들기
# 검색창에 보여줄 리스트: ["삼성전자 (005930.KS)", "엔비디아 (NVDA)", ...]
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 핵심 로직: 위젯 상태 관리 ---

# 현재 확정된 티커를 저장할 변수
if 'final_ticker' not in st.session_state:
    st.session_state['final_ticker'] = None

def on_search_select():
    """검색창에서 선택했을 때 실행"""
    selection = st.session_state.search_box
    if selection:
        # "엔비디아 (NVDA)" -> "NVDA" 추출
        ticker = selection.split('(')[-1].replace(')', '')
        st.session_state['final_ticker'] = ticker
        # (중요) 검색창 초기화 (다음을 위해)
        st.session_state.search_box = None

def on_input_change():
    """입력창 값을 수정하거나 지웠을 때 실행"""
    current_val = st.session_state.result_box
    
    # 텍스트를 다 지우면 -> 다시 검색 모드로 돌아감
    if not current_val:
        st.session_state['final_ticker'] = None
    # 텍스트를 수정하면 -> 수정한 값 유지
    else:
        st.session_state['final_ticker'] = current_val

# --- UI 구현 (마법의 위젯 교체) ---

st.title("⚡ 주식 티커 변환기")
st.write("기업명을 선택하면 입력창이 **티커**로 바뀝니다.")

# ★ placeholder: 이 빈 공간에 위젯을 번갈아 끼워 넣습니다.
placeholder = st.empty()

# [상황 A] 티커가 없을 때 -> 검색창(Selectbox) 보여주기
if st.session_state['final_ticker'] is None:
    with placeholder.container():
        st.selectbox(
            "종목 검색",
            options=search_options,
            index=None,
            placeholder="기업명을 입력하세요 (예: 엔비, 삼성...)",
            key="search_box",
            on_change=on_search_select, # 선택 즉시 실행
            label_visibility="collapsed" # 라벨을 숨겨서 깔끔하게
        )

# [상황 B] 티커가 있을 때 -> 텍스트창(Text Input) 보여주기
else:
    with placeholder.container():
        st.text_input(
            "티커",
            value=st.session_state['final_ticker'],
            key="result_box",
            on_change=on_input_change, # 수정 시 실행
            label_visibility="collapsed" # 라벨을 숨겨서 위 검색창과 똑같이 보이게 함
        )
        # 안내 문구 (작게)
        st.caption("🔄 다시 검색하려면 내용을 지우고 엔터를 누르세요.")


# --- 결과 차트 출력 ---
ticker = st.session_state['final_ticker']

if ticker:
    st.divider()
    if st.button(f"📈 '{ticker}' 차트 보기", type="primary"):
        with st.spinner('데이터 불러오는 중...'):
            try:
                # 사용자가 직접 입력한 소문자 등을 대문자로 변환
                clean_ticker = ticker.upper().strip()
                df = yf.download(clean_ticker, period="1mo", progress=False)
                
                if not df.empty:
                    st.line_chart(df['Close'])
                    st.success(f"현재가: {df['Close'].iloc[-1]:.2f}")
                else:
                    st.error("데이터를 찾을 수 없습니다.")
            except Exception as e:
                st.error(f"오류: {e}")
