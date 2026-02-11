import streamlit as st
import json

# 1. 페이지 설정
st.set_page_config(page_title="주식 티커 자동완성", page_icon="⚡")

# 2. 데이터 준비 (테스트 데이터 + JSON 로드)
@st.cache_data
def load_data():
    # 파일이 없어도 작동하도록 기본 데이터 내장
    default_data = [
        {"name_kr": "삼성전자", "ticker": "005930.KS"},
        {"name_kr": "SK하이닉스", "ticker": "000660.KS"},
        {"name_kr": "현대차", "ticker": "005380.KS"},
        {"name_kr": "엔비디아", "ticker": "NVDA"},
        {"name_kr": "테슬라", "ticker": "TSLA"},
        {"name_kr": "애플", "ticker": "AAPL"},
        {"name_kr": "마이크로소프트", "ticker": "MSFT"},
        {"name_kr": "구글(알파벳)", "ticker": "GOOGL"},
        {"name_kr": "아마존", "ticker": "AMZN"},
        {"name_kr": "넷플릭스", "ticker": "NFLX"},
        {"name_kr": "카카오", "ticker": "035720.KS"},
        {"name_kr": "네이버", "ticker": "035420.KS"},
    ]
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default_data

stock_list = load_data()

# 3. 데이터 검색 최적화 (빠른 조회를 위해 리스트 준비)
# 티커만 모아놓은 집합 (이미 선택된 상태인지 확인용)
all_tickers = {item['ticker'] for item in stock_list}

# --- 핵심 로직: 세션 상태 초기화 ---
if 'input_text' not in st.session_state:
    st.session_state['input_text'] = ""

# [함수] 추천 버튼 클릭 시 실행 -> 입력창을 티커로 변경
def select_ticker(ticker_value):
    st.session_state['input_text'] = ticker_value

# --- UI 구성 ---

st.title("⚡ 주식 티커 자동완성")
st.markdown("기업명을 입력하면 아래에 추천 목록이 뜹니다. 클릭하면 티커로 변환됩니다.")

# 1. 메인 입력창 (여기서 검색과 결과 표시를 모두 담당)
query = st.text_input(
    label="종목 검색 / 티커 입력",
    value=st.session_state['input_text'],
    placeholder="예: 삼성, 엔비, 테슬라...",
    key="input_field", 
    # 사용자가 타이핑할 때마다 session_state['input_text']가 업데이트되도록 함
    on_change=lambda: st.session_state.update({'input_text': st.session_state.input_field})
)

# 2. 자동완성 로직 (검색어가 있고, 아직 티커가 완성되지 않았을 때만 추천 목록 표시)
# 조건: 검색어가 있고(query) AND 검색어가 이미 완성된 티커가 아닐 때(query not in all_tickers)
if query and query not in all_tickers:
    
    # 검색어 필터링 (한글 이름이나 티커에 포함된 것 찾기)
    matches = [
        item for item in stock_list 
        if query.upper() in item['name_kr'] 
        or query.upper() in item['ticker']
    ]
    
    # 추천 목록 표시 (결과가 있을 때만)
    if matches:
        st.info("👇 아래에서 기업을 선택하세요")
        
        # 버튼을 나열 (최대 5개까지만 보여주기 - 너무 길어지면 보기 싫음)
        for item in matches[:5]:
            # 버튼 라벨: "삼성전자 (005930.KS)"
            btn_label = f"{item['name_kr']} ({item['ticker']})"
            
            # 버튼을 누르면 -> select_ticker 함수 실행 -> 입력창 값이 티커로 바뀜
            if st.button(btn_label, use_container_width=True):
                select_ticker(item['ticker'])
                st.rerun() # 화면 즉시 새로고침하여 입력창 업데이트

# --- 결과 처리 ---
# 현재 입력된 값이 '유효한 티커'라면 차트 표시
if query in all_tickers:
    st.success(f"✅ 선택된 티커: **{query}**")
    
    # 여기서부터 차트나 데이터를 보여주면 됩니다.
    st.divider()
    if st.button("차트 보기"):
        st.line_chart([10, 20, 15, 25, 30]) # 테스트용 차트
