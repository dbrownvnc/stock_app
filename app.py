import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="주식 티커 검색기", layout="centered")

# 2. 데이터 로드 (캐싱)
@st.cache_data
def load_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # 파일이 없을 경우 기본 데이터
        return [
            {"name_kr": "삼성전자", "ticker": "005930.KS"},
            {"name_kr": "SK하이닉스", "ticker": "000660.KS"},
            {"name_kr": "엔비디아", "ticker": "NVDA"},
            {"name_kr": "테슬라", "ticker": "TSLA"},
            {"name_kr": "애플", "ticker": "AAPL"},
            {"name_kr": "마이크로소프트", "ticker": "MSFT"},
            {"name_kr": "구글", "ticker": "GOOGL"},
            {"name_kr": "아마존", "ticker": "AMZN"}
        ]

stock_list = load_data()
search_options = [f"{s['name_kr']} ({s['ticker']})" for s in stock_list]

# --- 핵심 로직: 상태 관리 및 자동 리셋 ---

# 선택된 티커를 저장할 변수
if 'selected_ticker' not in st.session_state:
    st.session_state['selected_ticker'] = ""

def on_select():
    # 사용자가 리스트에서 선택했을 때 실행
    val = st.session_state.search_box
    if val:
        # "엔비디아 (NVDA)" -> "NVDA" 추출
        ticker = val.split('(')[-1].replace(')', '')
        st.session_state['selected_ticker'] = ticker
        
        # ★ 핵심 기능 ★
        # 선택 값을 저장한 뒤, 위젯의 값을 강제로 None(빈 상태)으로 초기화합니다.
        # 이렇게 하면 입력창은 항상 '검색 대기 상태'가 되어 언제든 클릭하면 리스트가 뜹니다.
        st.session_state.search_box = None

# --- UI 구현 ---

st.title("📈 주식 티커 검색")

# 현재 선택된 티커 확인
current_val = st.session_state['selected_ticker']

# Placeholder 문구를 동적으로 변경하여 '티커만 남은 효과'를 줍니다.
# 값이 있으면 그 티커를 보여주고, 없으면 검색 유도 문구를 보여줍니다.
if current_val:
    placeholder_text = f"✅ {current_val}"  # 여기에 티커가 표시됩니다.
else:
    placeholder_text = "기업명 또는 티커를 검색하세요..."

# 단일 입력창 (언제나 검색 활성화)
st.selectbox(
    label="종목 검색",
    options=search_options,
    index=None,            # 항상 선택되지 않은 상태 유지 (클릭 시 바로 리스트 뜸)
    placeholder=placeholder_text, # 선택된 티커가 여기에 보임
    key="search_box",
    on_change=on_select,   # 선택 즉시 실행
    label_visibility="collapsed"
)

# --- 결과 및 차트 출력 (오류 수정 완료) ---

if current_val:
    st.divider()
    try:
        # 데이터 다운로드
        with st.spinner(f"'{current_val}' 데이터 불러오는 중..."):
            df = yf.download(current_val, period="1mo", progress=False)
            
            if not df.empty:
                st.subheader(f"📊 {current_val} 차트")
                st.line_chart(df['Close'])
                
                # [오류 해결] Series 객체를 순수 float(실수)로 변환
                # yfinance 버전에 따라 iloc[-1]이 Series일 수도, scalar일 수도 있음
                last_price_raw = df['Close'].iloc[-1]
                
                try:
                    # .item()은 numpy 데이터타입을 파이썬 native float으로 변환해줌
                    current_price = float(last_price_raw.item())
                except:
                    # .item()이 안 먹히는 경우 일반 float 변환 시도
                    current_price = float(last_price_raw)

                # 이제 안전하게 포맷팅 가능
                st.metric("최근 종가", f"{current_price:,.2f}")
            else:
                st.error("데이터를 찾을 수 없습니다. (상장 폐지되었거나 티커가 변경되었을 수 있습니다)")
                
    except Exception as e:
        st.error(f"일시적인 오류가 발생했습니다: {e}")

# 사용 팁 안내 (선택적)
if not current_val:
    st.caption("💡 입력창을 클릭하여 종목을 검색해보세요.")
