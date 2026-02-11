import streamlit as st
import json
import yfinance as yf
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="주식 티커 검색기", page_icon="🔍")

# 2. 데이터 로드 (캐싱을 사용하여 속도 최적화)
@st.cache_data
def load_stock_data():
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("stocks.json 파일을 찾을 수 없습니다.")
        return []

stock_list = load_stock_data()

# 3. 검색을 위한 리스트 만들기 (UI에 보여질 문자열)
# 예: "삼성전자 (005930.KS) | KOSPI" 형태로 만듦
search_options = []
ticker_map = {} # 선택된 문자열로 원본 데이터를 찾기 위한 맵

for stock in stock_list:
    # 검색창에 보여질 텍스트 조합
    display_text = f"{stock['name_kr']} ({stock['ticker']}) - {stock['market']}"
    
    # 나중에 티커를 찾기 위해 저장
    search_options.append(display_text)
    ticker_map[display_text] = stock

# --- UI 구성 ---

st.title("📈 주식 티커 자동완성 검색")
st.markdown("한국/미국 주식명을 입력하면 **티커**로 변환해줍니다.")

# 4. 자동완성 검색창 (Selectbox 활용)
# 사용자가 "엔비"라고 치면, "엔비디아..."가 필터링되어 보임
selected_option = st.selectbox(
    label="종목을 검색하세요:",
    options=search_options,
    index=None, # 처음에 아무것도 선택 안 된 상태
    placeholder="예: 삼성, 엔비디아, 애플..."
)

st.divider()

# 5. 결과 처리
if selected_option:
    # 선택된 텍스트로 원본 데이터 조회
    stock_info = ticker_map[selected_option]
    ticker = stock_info['ticker']
    name = stock_info['name_kr']

    # 결과 보여주기
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"선택한 기업: **{name}**")
    with col2:
        st.success(f"티커 코드: **{ticker}**")

    # (추가기능) 실제 데이터 가져와보기
    st.subheader(f"{name} ({ticker}) 주가 차트")
    
    with st.spinner('데이터를 불러오는 중...'):
        try:
            # yfinance로 데이터 다운로드
            df = yf.download(ticker, period="1mo")
            if not df.empty:
                st.line_chart(df['Close'])
            else:
                st.warning("데이터를 불러올 수 없습니다.")
        except Exception as e:
            st.error(f"오류 발생: {e}")