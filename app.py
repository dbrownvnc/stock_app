import streamlit as st
from streamlit_searchbox import st_searchbox
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="Anytime Autocomplete", layout="centered")

# 2. 데이터 로드
@st.cache_data
def load_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # 테스트 데이터
        return [
            {"name_kr": "삼성전자", "ticker": "005930.KS"},
            {"name_kr": "SK하이닉스", "ticker": "000660.KS"},
            {"name_kr": "엔비디아", "ticker": "NVDA"},
            {"name_kr": "테슬라", "ticker": "TSLA"},
            {"name_kr": "애플", "ticker": "AAPL"},
            {"name_kr": "마이크로소프트", "ticker": "MSFT"}
        ]

stock_list = load_data()

# 3. [핵심] 검색 로직 함수
def search_engine(searchterm: str):
    # 검색어가 없으면 추천 리스트(상위 5개)를 보여줄 수도 있음
    # 여기서는 빈 리스트 반환
    if not searchterm:
        return []

    searchterm = searchterm.lower().strip()
    results = []

    for stock in stock_list:
        # [중요] 한글 이름이나 티커(소문자)에 검색어가 포함되면 결과에 추가
        # 예: 'nvda'를 입력해도 '엔비디아 (NVDA)'가 검색되도록 함
        if searchterm in stock['name_kr'].lower() or searchterm in stock['ticker'].lower():
            
            # [UI 핵심] 리스트에는 '이름+티커'를 보여주고,
            # 선택 시 입력창에는 '티커'만 남기도록 튜플(Label, Value)로 반환
            label = f"{stock['name_kr']} ({stock['ticker']})"
            value = stock['ticker']
            results.append((label, value))

    return results

# --- UI 구현 ---

st.title("⚡ Always-On 자동완성")
st.write("입력창을 클릭하면 **언제든** 자동완성 기능이 활성화됩니다.")

# 4. 자동완성 위젯
# key: 위젯 고유 ID
# edit_after_submit=True: 선택 후에도 텍스트 수정 모드가 유지됨 (클릭 시 재검색 가능)
selected_ticker = st_searchbox(
    search_engine,
    key="my_searchbox",
    placeholder="종목명 또는 티커 검색...",
    edit_after_submit=True,
)

# 5. 결과 처리 및 오류 수정
if selected_ticker:
    st.divider()
    
    # 리스트에 없는 임의의 값 입력 방지용 검증
    is_valid_ticker = any(s['ticker'] == selected_ticker for s in stock_list)

    if is_valid_ticker:
        try:
            with st.spinner(f"'{selected_ticker}' 차트 로딩 중..."):
                # yfinance 데이터 다운로드
                df = yf.download(selected_ticker, period="1mo", progress=False)
                
                if not df.empty:
                    st.subheader(f"📊 {selected_ticker} 주가 차트")
                    st.line_chart(df['Close'])
                    
                    # [오류 완벽 수정 구간]
                    # DataFrame/Series에서 값을 꺼낼 때 명시적으로 float 변환
                    last_val = df['Close'].iloc[-1]
                    try:
                        # .item()은 numpy 데이터타입을 파이썬 스칼라로 변환
                        current_price = float(last_val.item())
                    except:
                        # 구버전 pandas/numpy 호환
                        current_price = float(last_val)

                    st.metric("현재가", f"{current_price:,.2f}")
                else:
                    st.error("차트 데이터를 불러올 수 없습니다.")
        except Exception as e:
            st.error(f"데이터 처리 중 오류가 발생했습니다.")
    else:
        # 유효하지 않은 입력일 때
        if len(selected_ticker) > 0:
             st.warning("⚠️ 검색 결과 목록에서 종목을 선택해주세요.")

st.caption("💡 팁: 입력창에 티커가 있어도, 클릭하고 글자를 치면 바로 검색됩니다.")
