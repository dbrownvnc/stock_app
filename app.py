import streamlit as st
import json
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="주식 티커 검색기", page_icon="🔍")

# 2. 데이터 로드
@st.cache_data
def load_stock_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("stocks.json 파일을 찾을 수 없습니다.")
        return []

stock_list = load_stock_data()

# --- 핵심 로직: 포맷팅 함수 만들기 ---

# 3. 딕셔너리 생성 (Ticker -> 보여줄 이름)
# 기계는 Ticker(키)를 갖고 놀고, 사람은 Value(이름)를 봅니다.
ticker_dict = {}

for stock in stock_list:
    # 딕셔너리 형태: {'NVDA': '엔비디아 (NVDA)', '005930.KS': '삼성전자 (005930.KS)'}
    display_name = f"{stock['name_kr']} ({stock['ticker']})" 
    ticker_dict[stock['ticker']] = display_name

# 4. 화면에 이름을 보여주는 함수 (format_func용)
def format_option(ticker):
    return ticker_dict.get(ticker, ticker)


# --- UI 구성 ---

st.title("🔍 스마트 티커 검색기")
st.markdown("기업명을 선택하면 **티커(Ticker)**만 깔끔하게 입력됩니다.")

col1, col2 = st.columns([2, 1])

with col1:
    # [A] 검색창 (Selectbox)
    # options에는 실제 값인 '티커' 리스트를 넣습니다.
    # format_func가 티커를 받아 '한글 이름'으로 바꿔서 보여줍니다.
    selected_ticker = st.selectbox(
        "기업 검색 (한글/영문)",
        options=list(ticker_dict.keys()), # 실제 값: ['NVDA', 'AAPL', ...]
        format_func=format_option,        # 화면 표시: '엔비디아 (NVDA)'
        index=None,
        placeholder="종목을 선택하세요..."
    )

with col2:
    # [B] 결과 확인창 (Text Input)
    # 위에서 선택된 값(selected_ticker)이 자동으로 여기에 꽂힙니다.
    # 사용자가 직접 수정할 수도 있습니다.
    final_ticker = st.text_input(
        "티커 코드",
        value=selected_ticker if selected_ticker else ""
    )

st.divider()

# --- 결과 출력 ---
if final_ticker:
    st.subheader(f"📈 {final_ticker} 실시간 차트")
    
    if st.button("차트 불러오기"):
        with st.spinner('데이터 수신 중...'):
            try:
                # 사용자가 직접 입력한 경우를 대비해 공백 제거 및 대문자 변환
                clean_ticker = final_ticker.strip().upper()
                
                df = yf.download(clean_ticker, period="1mo", progress=False)
                
                if not df.empty:
                    st.line_chart(df['Close'])
                    
                    # 현재가 정보 표시
                    last_price = df['Close'].iloc[-1]
                    # last_price가 스칼라(숫자)인지 Series인지 확인하여 처리
                    try:
                        price_val = last_price.item() # 숫자만 추출
                    except:
                        price_val = last_price

                    st.metric(label="현재 주가", value=f"{price_val:,.2f}")
                else:
                    st.error(f"'{clean_ticker}'에 대한 데이터가 없습니다.")
            except Exception as e:
                st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
