import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="Pro Ticker Search", layout="centered")

# 2. 데이터 로드 (캐싱 적용)
@st.cache_data
def load_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return [
            {"name_kr": "삼성전자", "ticker": "005930.KS"},
            {"name_kr": "SK하이닉스", "ticker": "000660.KS"},
            {"name_kr": "엔비디아", "ticker": "NVDA"},
            {"name_kr": "테슬라", "ticker": "TSLA"},
            {"name_kr": "애플", "ticker": "AAPL"},
            {"name_kr": "마이크로소프트", "ticker": "MSFT"},
            {"name_kr": "아마존", "ticker": "AMZN"},
            {"name_kr": "구글", "ticker": "GOOGL"},
        ]

stock_list = load_data()

# 기본 검색 옵션 리스트 생성 ["삼성전자 (005930.KS)", ...]
base_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 핵심 로직: 상태 관리 및 동적 옵션 생성 ---

if 'selected_ticker' not in st.session_state:
    st.session_state['selected_ticker'] = None

# 위젯 값이 변경될 때 실행되는 함수
def on_change():
    value = st.session_state.search_box
    
    if value:
        # 선택된 값이 "삼성전자 (005930.KS)" 형태라면 티커만 추출
        if "(" in value and ")" in value:
            ticker = value.split('(')[-1].replace(')', '')
        else:
            # 이미 티커 형태("NVDA")라면 그대로 유지
            ticker = value
            
        st.session_state['selected_ticker'] = ticker
    else:
        # X 버튼을 눌러 지운 경우
        st.session_state['selected_ticker'] = None

# [마법의 로직]
# 현재 선택된 티커가 있다면, 그 티커를 옵션 리스트의 맨 앞에 '강제로' 추가합니다.
# 이렇게 하면 selectbox는 'NVDA'라는 값을 선택한 상태로 렌더링되므로
# 화면에는 긴 이름 대신 'NVDA'만 깔끔하게 보입니다.
if st.session_state['selected_ticker']:
    current_ticker = st.session_state['selected_ticker']
    # 화면 표시용 옵션 리스트 = [현재 티커] + [원래 검색 리스트]
    display_options = [current_ticker] + base_options
    default_index = 0 # 맨 앞에 넣었으므로 인덱스는 0
else:
    display_options = base_options
    default_index = None # 선택된 게 없으면 빈칸

# --- UI 구현 ---

st.title("⚡ 실시간 티커 검색기")
st.write("이름으로 검색하고, 티커만 확인하세요. **클릭하면 바로 재검색** 됩니다.")

# 단 하나의 위젯으로 모든 기능 통합
st.selectbox(
    label="종목 검색",
    options=display_options,     # 동적으로 변하는 옵션 리스트
    index=default_index,         # 선택된 티커가 있으면 그걸 가리킴
    placeholder="기업명 또는 티커를 입력하세요...",
    key="search_box",
    on_change=on_change,
    label_visibility="collapsed" # 라벨 숨김 (깔끔하게)
)

# --- 차트 및 데이터 출력 ---
final_ticker = st.session_state['selected_ticker']

if final_ticker:
    st.divider()
    try:
        # 데이터 로딩
        with st.spinner(f"Running Analysis for {final_ticker}..."):
            df = yf.download(final_ticker, period="1mo", progress=False)
            
            if not df.empty:
                # 차트 출력
                st.subheader(f"📊 {final_ticker} Chart")
                st.line_chart(df['Close'])
                
                # 현재가 출력 (포맷팅 오류 방지 코드 포함)
                last_val = df['Close'].iloc[-1]
                try:
                    price = float(last_val.item()) # Series -> float 변환
                except:
                    price = float(last_val)
                    
                st.metric("Current Price", f"{price:,.2f}")
            else:
                st.warning("데이터를 불러올 수 없습니다. 티커를 확인해주세요.")
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")

# 사용 팁 안내 (하단 고정)
st.caption("💡 **Tip:** 입력창에 `NVDA`가 있어도 클릭하고 `삼`을 치면 즉시 삼성전자가 검색됩니다.")
