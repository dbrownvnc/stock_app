import streamlit as st
from streamlit_searchbox import st_searchbox
import json
import yfinance as yf
import uuid

# 1. 페이지 설정
st.set_page_config(page_title="티커 검색 마스터", layout="centered")

# 2. 데이터 로드
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
            {"name_kr": "애플", "ticker": "AAPL"},
            {"name_kr": "마이크로소프트", "ticker": "MSFT"}
        ]

stock_list = load_data()

# 3. 검색 로직 (이름+티커 검색 -> 리스트 표시)
def search_stock(searchterm: str):
    if not searchterm:
        return []

    searchterm = searchterm.lower().strip()
    results = []

    for stock in stock_list:
        # 이름이나 티커로 검색
        if searchterm in stock['name_kr'].lower() or searchterm in stock['ticker'].lower():
            # 리스트에는 "이름 (티커)" 형태로 보여줌
            label = f"{stock['name_kr']} ({stock['ticker']})"
            # 실제 값은 "티커"만 전달
            value = stock['ticker']
            results.append((label, value))

    return results

# --- 핵심 로직: 세션 상태 및 키 관리 ---

# 검색창을 강제로 리셋하기 위한 고유 키 관리
if 'search_box_key' not in st.session_state:
    st.session_state['search_box_key'] = str(uuid.uuid4())

if 'last_ticker' not in st.session_state:
    st.session_state['last_ticker'] = ""

# 검색창에서 값이 선택되었을 때 실행되는 로직
def on_change_search():
    # 현재 위젯의 키를 통해 값을 가져옴
    current_key = st.session_state['search_box_key']
    
    # st_searchbox는 선택된 값이 session_state에 저장됨
    if current_key in st.session_state:
        selected_val = st.session_state[current_key]
        
        # 값이 선택되었다면?
        if selected_val:
            st.session_state['last_ticker'] = selected_val
            # ★ 핵심: 키를 변경하여 위젯을 강제로 새로고침 (입력값을 티커로 덮어쓰기 위함)
            st.session_state['search_box_key'] = str(uuid.uuid4())

# --- UI 구현 ---

st.title("⚡ 주식 티커 자동완성")
st.write("입력창을 클릭하면 언제든 자동완성이 활성화됩니다.")

# 4. 스마트 검색창
# default 값에 last_ticker를 넣어주어, 리로딩될 때 티커가 입력창에 박히게 함
ticker_input = st_searchbox(
    search_stock,
    key=st.session_state['search_box_key'], # 동적 키 사용
    default=st.session_state['last_ticker'], # 선택된 티커를 기본값으로 설정
    placeholder="기업명 검색 (예: 삼성, 엔비...)",
    edit_after_submit=True, # 선택 후 즉시 수정 가능
    on_change=on_change_search # 선택 감지 시 키 변경 로직 실행
)

# 5. 차트 및 데이터 출력 (오류 수정됨)
if st.session_state['last_ticker']:
    target_ticker = st.session_state['last_ticker']
    st.divider()
    
    try:
        with st.spinner(f"'{target_ticker}' 차트 로딩 중..."):
            # 데이터 수집
            df = yf.download(target_ticker, period="1mo", progress=False)
            
            if not df.empty:
                st.subheader(f"📊 {target_ticker} 분석")
                st.line_chart(df['Close'])
                
                # [오류 해결] Series -> float 변환 후 포맷팅
                last_val = df['Close'].iloc[-1]
                try:
                    # .item()은 numpy 데이터타입일 경우 파이썬 스칼라로 변환
                    price = float(last_val.item())
                except:
                    price = float(last_val)

                st.metric("최근 종가", f"{price:,.2f}")
            else:
                st.warning("데이터를 찾을 수 없습니다. 올바른 티커인지 확인해주세요.")
                
    except Exception as e:
        # yfinance 일시적 오류 등이 발생할 수 있으므로 예외 처리
        st.error("데이터 통신 중 오류가 발생했습니다.")
