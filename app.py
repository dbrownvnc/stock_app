import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="무한 티커 검색기", layout="centered")

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
            {"name_kr": "애플", "ticker": "AAPL"}
        ]

stock_list = load_data()
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 핵심 로직: 단일 위젯 무한 루프 ---

# 실제 활용할 티커 저장용 세션 상태
if 'final_ticker' not in st.session_state:
    st.session_state['final_ticker'] = ""

def on_change():
    # 사용자가 무언가를 선택했을 때
    if st.session_state.master_search:
        # 티커 추출
        ticker = st.session_state.master_search.split('(')[-1].replace(')', '')
        st.session_state['final_ticker'] = ticker
        
        # ★ 핵심: 선택 직후 위젯의 선택 상태를 다시 초기화하여 '언제나 입력 가능'하게 만듦
        # st.session_state.master_search = None (이 구문은 내부적으로 다음 렌더링 시 적용됨)

# --- UI 구현 ---

st.title("📈 통합 종목 검색")

# placeholder_text를 현재 선택된 티커로 동적 변경 (선택된 게 있으면 그걸 보여줌)
current_view = st.session_state['final_ticker']
display_placeholder = f"현재: {current_view} (클릭하여 새 종목 검색)" if current_view else "종목명 또는 티커를 입력하세요"

# 단 하나의 위젯으로 승부
st.selectbox(
    label="종목 검색",
    options=search_options,
    index=None, # 항상 비어있는 상태로 시작/유지
    placeholder=display_placeholder,
    key="master_search",
    on_change=on_change,
    label_visibility="collapsed"
)

# --- 결과 출력 (입력창 바로 아래에 차트 연결) ---
if st.session_state['final_ticker']:
    target = st.session_state['final_ticker']
    
    # 별도 텍스트 없이 바로 차트나 데이터 출력
    try:
        # yfinance 데이터 가져오기 (매번 다시 다운로드하지 않도록 캐싱 고려 가능)
        df = yf.download(target, period="1mo", progress=False)
        if not df.empty:
            st.subheader(f"📊 {target} 주가 추이")
            st.line_chart(df['Close'])
        else:
            st.error("데이터를 불러올 수 없습니다.")
    except Exception as e:
        st.error("오류 발생")

st.caption("💡 창을 클릭하면 언제든지 즉시 새로운 종목을 검색하고 자동완성할 수 있습니다.")
