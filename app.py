import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# -------------------------------------------------
# 페이지 설정 (사이드바 제거, 전체 화면을 넓고 꽉 차게 설정)
# -------------------------------------------------
st.set_page_config(
    page_title="항공기 엔진 정밀 상태 진단 시스템",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# [핵심] Streamlit 자체 요소를 칼정렬하는 커스텀 CSS
# -------------------------------------------------
st.markdown("""
<style>
/* 전체 화면 설정 및 배경 정돈 */
.stApp {
    background-color: #F8FAFC; 
    font-family: -apple-system, BlinkMacSystemFont, "Malgun Gothic", sans-serif;
}

.block-container {
    padding-top: 2.0rem;
    padding-bottom: 2.0rem;
}

/* 상단 타이틀 */
.main-title {
    text-align: center;
    color: #0F172A;
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 6px;
}

.sub-title {
    text-align: center;
    color: #64748B;
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 35px;
}

/* -------------------------------------------------
   [구조 개혁] Streamlit Column을 활용한 자동 바둑판 격자 스타일
   ------------------------------------------------- */
/* 개별 센서 조절 칸을 흰색 카드 형태로 일체화 */
div[data-testid="stVerticalBlock"] > div[data-testid="stColumn"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    padding: 20px !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02) !important;
}

/* 슬라이더 내부 타이틀 폰트 스타일 지정 */
div[data-testid="stWidgetLabel"] p {
    font-size: 13px !important;
    font-weight: 700 !important;
    color: #1E3A8A !important; /* 가독성 높은 네이비 컬러 */
    margin-bottom: 4px !important;
}

/* 하단 안전 범위 가이드 안내 텍스트 */
.range-info {
    font-size: 11px;
    color: #64748B;
    font-weight: 600;
    margin-top: -6px;
    margin-bottom: 5px;
    background-color: #F8FAFC;
    padding: 5px 10px;
    border-radius: 4px;
    border-left: 3px solid #94A3B8;
}

/* 노후 계통 가이드 전용 강조 색상 */
.range-alert {
    border-left-color: #EF4444;
    background-color: #FEF2F2;
    color: #991B1B;
}

/* -------------------------------------------------
   우측 통합 진단 결과창 전용 스타일 (깨짐 및 겹침 방지)
   ------------------------------------------------- */
.report-container {
    background-color: #FFFFFF;
    border: 1px solid #94A3B8;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.04);
}

.report-title {
    font-size: 14px;
    font-weight: 800;
    color: #475569;
    margin-bottom: 12px;
    letter-spacing: -0.3px;
}

/* 대형 합격/불합격 판정 플록 */
.status-block {
    padding: 14px;
    border-radius: 6px;
    text-align: center;
    font-weight: 800;
    font-size: 17px;
    margin-bottom: 25px;
}

.status-normal {
    background-color: #E8F5E9;
    color: #2E7D32;
    border: 1px solid #C8E6C9;
}

.status-critical {
    background-color: #FFEBEE;
    color: #C62828;
    border: 1px solid #FFCDD2;
}

/* 정비 권고 사항 글머리 리스트 */
.guide-list {
    margin: 0;
    padding-left: 18px;
    font-size: 12px;
    color: #334155;
    line-height: 1.6;
    font-weight: 500;
}

.guide-list li {
    margin-bottom: 8px;
}

/* -------------------------------------------------
   중앙 예측 실행 버튼 스타일
   ------------------------------------------------- */
.stButton button {
    width: 100%;
    height: 52px;
    font-size: 16px;
    font-weight: 800;
    border-radius: 6px;
    background-color: #1E3A8A !important;
    color: #FFFFFF !important;
    border: 1px solid #1D4ED8 !important;
    box-shadow: 0 4px 6px rgba(30, 58, 138, 0.1);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 예측 알고리즘 파일 로드 (예외 처리 포함)
# -------------------------------------------------
try:
    모델 = joblib.load("aircraft_model.pkl")
    스케일러 = joblib.load("aircraft_scaler.pkl")
    model_loaded = True
except:
    model_loaded = False

# -------------------------------------------------
# 메인 헤더
# -------------------------------------------------
st.markdown("<div class='main-title'>항공기 엔진 상태 예측 진단 플랫폼</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>실시간 제어 계통 데이터 통합 모니터링 및 상태 추론 대시보드</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 메인 구역 레이아웃 배치 (좌측 센서 바둑판 70% : 우측 결과 보드 30%)
# -------------------------------------------------
메인좌측, 메인우측 = st.columns([2.3, 1.0], gap="medium")

with 메인좌측:
    st.markdown("<div style='font-size:15px; font-weight:800; color:#0F172A; margin-bottom:18px; border-left:4px solid #1E3A8A; padding-left:10px;'>원격 측정 계통 데이터 입력</div>", unsafe_allow_html=True)
    
    # 1행 바둑판 (가동 지표, 저압 계통 온도, 저압 계통 유량)
    행1_열1, 행1_열2, 행1_열3 = st.columns(3)
    with 행1_열1:
        운전사이클 = st.slider("누적 구동 사이클", 1, 400, 232)
        st.markdown("<div class='range-info range-alert'>기준 수치: 200 사이클 초과 노후</div>", unsafe_allow_html=True)
    with 행1_열2:
        센서2 = st.slider("저압 압축기 출구 온도", 630.0, 650.0, 641.0)
        st.markdown("<div class='range-info'>안전 범위: 635.0 ~ 645.0 K</div>", unsafe_allow_html=True)
    with 행1_열3:
        센서21 = st.slider("저압 터빈 배출 유량", 20.0, 30.0, 23.0)
        st.markdown("<div class='range-info'>안전 범위: 22.5 ~ 24.5 lbm/s</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

    # 2행 바둑판 (고압 계통 온도 03, 고압 계통 온도 04, 고압 압축기 압력)
    행2_열1, 행2_열2, 행2_열3 = st.columns(3)
    with 행2_열1:
        센서3 = st.slider("고압 압축기 출구 온도", 1500.0, 1700.0, 1580.0)
        st.markdown("<div class='range-info'>안전 범위: 1560.0 ~ 1610.0 K</div>", unsafe_allow_html=True)
    with 행2_열2:
        센서4 = st.slider("저압 터빈 출구 온도", 1300.0, 1450.0, 1400.0)
        st.markdown("<div class='range-info'>안전 범위: 1380.0 ~ 1420.0 K</div>", unsafe_allow_html=True)
    with 행2_열3:
        센서7 = st.slider("고압 압축기 출구 압력", 500.0, 600.0, 550.0)
        st.markdown("<div class='range-info'>안전 범위: 540.0 ~ 565.0 psia</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

    # 3행 바둑판 (바이패스 덕트 압력, 바이패스 비율, 고압 터빈 속도, 고압 터빈 유량)
    # 깔끔한 3열 배치를 유지하기 위해 마지막 열에 슬라이더 2개를 통합 배치
    행3_열1, 행3_열2, 행3_열3 = st.columns(3)
    with 행3_열1:
        센서12 = st.slider("바이패스 덕트 압력", 8000.0, 8500.0, 8150.0)
        st.markdown("<div class='range-info'>안전 범위: 8100.0 ~ 8250.0 psia</div>", unsafe_allow_html=True)
        센서15 = st.slider("바이패스 유량 비율", 7.0, 10.0, 8.5)
        st.markdown("<div class='range-info'>안전 범위: 8.2 ~ 8.8</div>", unsafe_allow_html=True)
    with 행3_열2:
        센서11 = st.slider("고압 터빈 회전 속도", 2300.0, 2500.0, 2400.0)
        st.markdown("<div class='range-info'>안전 범위: 2370.0 ~ 2430.0 rpm</div>", unsafe_allow_html=True)
    with 행3_열3:
        센서20 = st.slider("고압 터빈 배출 유량", 35.0, 50.0, 40.0)
        st.markdown("<div class='range-info'>안전 범위: 38.0 ~ 42.0 lbm/s</div>", unsafe_allow_html=True)

    # 하단 배치 제어 버튼
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    진단가동버튼 = st.button("시스템 상태 예측 연산 기동")

with 메인우측:
    # 연산 로직 처리 수행
    if model_loaded:
        입력값 = pd.DataFrame(
            [[운전사이클, 센서2, 센서3, 센서4, 센서7, 센서11, 센서12, 센서15, 센서20, 센서21]],
            columns=['운전사이클', '센서2', '센서3', '센서4', '센서7', '센서11', '센서12', '센서15', '센서20', '센서21']
        )
        입력값 = 스케일러.transform(입력값)
        결과 = 모델.predict(입력값)[0]
        확률 = 모델.predict_proba(입력값)[0][1] if hasattr(모델, "predict_proba") else 0.5
    else:
        결과 = 1 if 운전사이클 > 210 else 0
        확률 = min(0.99, max(0.01, (운전사이클 / 380.0) + (센서3-1580)/800.0 - (센서7-550)/400.0))

    if 결과 == 1:
        배너텍스트, 배너클래스 = "정비 권고 (불합격)", "status-banner-critical"
        정비지침 = [
            "내부 컴포넌트의 가속 열화 상태가 감지되었습니다.",
            "즉시 작동 시퀀스를 중단 조치하십시오.",
            "엔진 정비 매뉴얼 지침에 따라 비파괴 검사를 수행하십시오."
        ]
    else:
        배너텍스트, 배너클래스 = "정상 가동 (합격)", "status-banner-normal"
        정비지침 = [
            "모든 가동 제어 계수의 거동이 신뢰 범위 내에 있습니다.",
            "계측 데이터의 이상 특이 징후가 발견되지 않았습니다.",
            "표준 규격에 계획된 정기 예방 정비 주기를 유지하십시오."
        ]

    # [수정 완료] 노출되던 고장 확률도 텍스트 태그를 완전히 제거하고 통합 박스로 마감
    st.markdown(f"""
    <div class='report-container'>
        <div class='report-title'>종합 진단 결과 판정</div>
        <div class='status-block {배너클래스}'>{배너텍스트}</div>
    </div>
    """, unsafe_allow_html=True)

    # 겹침 현상을 막기 위해 차트 백그라운드를 투명화하고 마진을 최적화하여 중간 삽입
    게이지_차트 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=확률 * 100,
        number={'suffix': "%", 'font': {'size': 26, 'weight': 'bold', 'color': '#0F172A'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': dict(size=8)},
            'bar': {'color': "#1E3A8A"},
            'bgcolor': "#F1F5F9",
            'steps': [
                {'range': [0, 35], 'color': 'rgba(16, 185, 129, 0.15)'},
                {'range': [35, 70], 'color': 'rgba(245, 158, 11, 0.15)'},
                {'range': [70, 100], 'color': 'rgba(239, 68, 68, 0.15)'}
            ]
        }
    ))
    게이지_차트.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=130, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(게이지_차트, use_container_width=True)

    # 하단 조치사항 리스트 연결 처리
    리스트_요소 = "".join([f"<li>{지침}</li>" for 지침 in 정비지침])
    st.markdown(f"""
    <div class='report-container' style='border-top: none; border-top-left-radius: 0; border-top-right-radius: 0; margin-top: -30px; padding-top: 5px;'>
        <div class='report-title' style='border-top: 1px solid #F1F5F9; padding-top: 15px; margin-bottom: 10px;'>엔진 계통 정비 권고사항</div>
        <ul class='guide-list'>
            {리스트_요소}
        </ul>
    </div>
    """, unsafe_allow_html=True)
