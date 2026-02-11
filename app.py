import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="주식 티커 자동완성", page_icon="⚡")

# 2. 데이터 준비
@st.cache_data
def load_data():
    # stock.json 파일이 없으면 기본 데이터 사용
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

# 3. 검색용 옵션 리스트 생성 ["삼성전자 (005930.KS)", "엔비디아 (NVDA)", ...]
# 검색창에서 보여줄 문자열들입니다.
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 핵심 로직: 상태 관리 (State Machine) ---

# 현재 확정된 티커가 있는지 확인 (없으면 None)
if 'final_ticker' not in st.session_state:
    st.session_state['final_ticker'] = None

# [1] 검색창에서 선택했을 때 실행되는 함수
def on_search_select():
    # 검색창(search_box)의 현재 값을 가져옴
    selection = st.session_state.search_box
    if selection:
        # "엔비디아 (NVDA)" -> "NVDA" 추출
        extracted_ticker = selection.split('(')[-1].replace(')', '')
        
        # 상태 업데이트: 티커 확정
        st.session_state['final_ticker'] = extracted_ticker
        
        # (중요) 검색창 상태 초기화: 나중에 돌아올 때를 위해 비워둠
        st.session_state.search_box = None 

# [2] 입력창 값을 변경하거나 지웠을 때 실행되는 함수
def on_input_change():
    # 입력창(result_box)의 현재 값을 가져옴
    current_val = st.session_state.result_box
    
    if not current_val:
        # 값을 다 지웠다면? -> 다시 검색 모드로 복귀
        st.session_state['final_ticker'] = None
    else:
        # 값을 수정했다면? -> 수정된 값 유지
        st.session_state['final_ticker'] = current_val

# --- UI 구현 (같은 위치에 위젯 교체) ---

st.title("⚡ 주식 티커 변환기")
st.write("기업명을 선택하면 티커로 변환됩니다.")

# 위젯이 들어갈 자리 (컨테이너)
input_placeholder = st.empty()

# [상태 A] 티커가 없을 때 -> 검색창(Selectbox) 표시
if st.session_state['final_ticker'] is None:
    with input_placeholder:
        st.selectbox(
            "종목 검색",
            options=search_options,
            index=None,  # 초기 상태는 빈 칸
            placeholder="기업명을 입력하세요 (예: 엔비, 삼성...)",
            key="search_box",  # 이 키를 통해 on_search_select에서 값을 읽음
            on_change=on_search_select, # 선택 즉시 실행
            label_visibility="collapsed" # 라벨 숨김 (깔끔하게)
        )

# [상태 B] 티커가 있을 때 -> 입력창(Text Input) 표시
else:
    with input_placeholder:
        st.text_input(
            "티커",
            value=st.session_state['final_ticker'], # 확정된 티커 표시
            key="result_box", # 이 키를 통해 on_input_change에서 값을 읽음
            on_change=on_input_change, # 수정하거나 지우면 실행
            label_visibility="collapsed"
        )
        # 입력창 아래에 안내 문구
        st.caption("✅ 티커가 입력되었습니다. (내용을 지우고 엔터를 치면 다시 검색합니다)")


# --- 결과 출력 ---
final_ticker = st.session_state['final_ticker']

if final_ticker:
    st.divider()
    if st.button("차트 보기"):
        with st.spinner(f"{final_ticker} 데이터 조회 중..."):
            try:
                df = yf.download(final_ticker, period="1mo", progress=False)
                if not df.empty:
                    st.line_chart(df['Close'])
                    st.success(f"현재가: {df['Close'].iloc[-1]:.2f}")
                else:
                    st.error("데이터를 찾을 수 없습니다.")
            except:
                st.error("티커를 확인해주세요.")
