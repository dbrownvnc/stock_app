import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="스마트 티커 검색", page_icon="⚡")

# 2. 데이터 로드
@st.cache_data
def load_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        # 테스트용 데이터
        data = [
            {"name_kr": "삼성전자", "ticker": "005930.KS"},
            {"name_kr": "엔비디아", "ticker": "NVDA"},
            {"name_kr": "테슬라", "ticker": "TSLA"},
            {"name_kr": "애플", "ticker": "AAPL"},
        ]
    return data

stock_list = load_data()

# 3. 검색용 옵션 만들기
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 핵심 로직: 선택 후 자동 초기화 ---

if 'confirmed_ticker' not in st.session_state:
    st.session_state['confirmed_ticker'] = None

def on_stock_select():
    # 사용자가 선택한 값 가져오기
    selection = st.session_state.search_box
    
    if selection:
        # 1. 티커 추출 ("엔비디아 (NVDA)" -> "NVDA")
        ticker = selection.split('(')[-1].replace(')', '')
        
        # 2. 결과 확정 (이 변수는 차트 그릴 때 사용)
        st.session_state['confirmed_ticker'] = ticker
        
        # 3. ★ 핵심 ★: 검색창을 강제로 비워버림 (재입력 가능 상태로 만듦)
        st.session_state.search_box = None

# --- UI 구현 ---

st.title("⚡ 스마트 티커 자동완성")
st.markdown("티커가 완성된 후 **바로 타이핑**하면 새로 검색됩니다.")

# 동적 Placeholder 생성
# 선택된 티커가 있으면 그것을 보여주고, 없으면 검색 유도 문구를 보여줌
if st.session_state['confirmed_ticker']:
    # [상태 A] 이미 선택된 상태 -> "NVDA (입력시 사라짐)" 표시
    placeholder_text = f"✅ {st.session_state['confirmed_ticker']} (다시 검색하려면 타이핑하세요)"
else:
    # [상태 B] 초기 상태
    placeholder_text = "기업명을 검색하세요..."

# 검색창 (Selectbox)
st.selectbox(
    label="종목 검색",
    options=search_options,
    index=None,  # 항상 선택되지 않은 상태(빈 상태)로 유지
    placeholder=placeholder_text, # 여기에 마법이 숨어있음
    key="search_box",
    on_change=on_stock_select, # 선택 즉시 실행
    label_visibility="collapsed"
)

st.divider()

# --- 결과 처리 ---
final_ticker = st.session_state['confirmed_ticker']

if final_ticker:
    # 실제 선택된 데이터가 활용되는 부분
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("선택된 티커", final_ticker)
    
    with col2:
        if st.button(f"{final_ticker} 차트 조회"):
            try:
                df = yf.download(final_ticker, period="1mo", progress=False)
                if not df.empty:
                    st.line_chart(df['Close'])
                else:
                    st.error("데이터 없음")
            except:
                st.error("조회 실패")
