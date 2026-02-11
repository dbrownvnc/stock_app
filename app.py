import streamlit as st
import json

# 1. 페이지 설정
st.set_page_config(page_title="주식 티커 검색기", page_icon="🔍")

# 2. 데이터 준비
@st.cache_data
def load_data():
    # 파일이 없으면 이 기본 데이터를 씁니다.
    default_data = [
        {"name_kr": "삼성전자", "ticker": "005930.KS"},
        {"name_kr": "SK하이닉스", "ticker": "000660.KS"},
        {"name_kr": "엔비디아", "ticker": "NVDA"},
        {"name_kr": "테슬라", "ticker": "TSLA"},
        {"name_kr": "애플", "ticker": "AAPL"},
        {"name_kr": "마이크로소프트", "ticker": "MSFT"},
        {"name_kr": "카카오", "ticker": "035720.KS"},
        {"name_kr": "네이버", "ticker": "035420.KS"},
    ]
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default_data

stock_list = load_data()

# 3. 검색용 데이터 구조 만들기
# (보여줄 이름) -> (실제 티커) 매핑
name_to_ticker = {f"{s['name_kr']} ({s['ticker']})": s['ticker'] for s in stock_list}
# (실제 티커) -> (보여줄 이름) 매핑 (역방향 검색용)
ticker_to_name = {v: k for k, v in name_to_ticker.items()}

# --- 핵심 로직: 세션 상태 관리 ---

if 'selected_value' not in st.session_state:
    st.session_state['selected_value'] = None

def on_change():
    """사용자가 리스트에서 무언가 선택했을 때 실행"""
    selection = st.session_state.stock_selector
    
    if selection:
        # 선택된 항목이 '이름(티커)' 형태라면 -> '티커'만 추출해서 저장
        if selection in name_to_ticker:
            st.session_state['selected_value'] = name_to_ticker[selection]
        # 이미 티커 형태라면 그대로 유지
        else:
            st.session_state['selected_value'] = selection

# --- UI 구현 ---

st.title("⚡ 주식 티커 자동 변환기")
st.markdown("기업명을 선택하면 티커로 변환됩니다. **다시 검색하려면 지우고 입력하세요.**")

# 여기서 중요! 
# options에는 [모든 검색 가능한 이름들] + [현재 선택된 티커]를 합쳐서 넣습니다.
# 그래야 'NVDA'가 선택된 상태에서도 리스트에 'NVDA'가 존재하여 에러가 안 납니다.

current_selection = st.session_state['selected_value']

# 옵션 리스트 준비
options = list(name_to_ticker.keys())

# 만약 현재 선택된 값이 티커(NVDA)라면, 옵션 리스트에 잠시 추가해줌 (UI 표시용)
if current_selection and current_selection not in options:
    options.insert(0, current_selection)

# ★ 하나의 Selectbox로 모든 걸 처리합니다.
final_ticker = st.selectbox(
    label="종목 검색 및 티커 확인",
    options=options,
    index=0 if current_selection else None, # 선택된 값이 있으면 그걸 보여줌
    placeholder="검색어를 입력하세요...",
    key="stock_selector",
    on_change=on_change # 값이 바뀌면 즉시 변환 로직 실행
)

# --- 결과 출력 ---
st.divider()

if final_ticker:
    # 만약 사용자가 선택한 값이 '이름(티커)' 형태라면 티커만 발라냄
    real_ticker = name_to_ticker.get(final_ticker, final_ticker)
    
    st.subheader(f"✅ 선택된 티커: {real_ticker}")
    
    # 여기서 yfinance 차트 그리기
    # import yfinance as yf
    # st.line_chart(yf.download(real_ticker, period='1mo')['Close'])
    
    # 팁: 사용자가 다시 검색하고 싶으면 selectbox의 X 버튼을 누르면 됩니다.
