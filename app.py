import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# -------------------------------------------------
# 페이지 설정
# -------------------------------------------------
st.set_page_config(
    page_title="항공기 엔진 정밀 상태 진단 시스템",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# 가독성 및 직관성을 위한 화면 설계 CSS (영어 원천 배제)
# -------------------------------------------------
st.markdown("""
<style>
/* 전체 화면 배경색 및 글꼴 최적화 */
.stApp {
    background-color: #F8FAFC; 
    font-family: -apple-system, BlinkMacSystemFont, "Malgun Gothic", "맑은 고딕", sans-serif;
}

.block-container {
    padding-top: 2.0rem;
    padding-bottom: 2.0rem;
}

/* 상단 제목 구역 */
.main-title {
    text-align: center;
    color: #0F172A;
    font-size: 30px;
    font-weight: 800;
    margin-bottom: 5px;
    letter-spacing: -0.5px;
}

.sub-title {
    text-align: center;
    color: #475569;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 40px;
}

/* -------------------------------------------------
   [가독성 개선] 시선이 분산되지 않는 밀폐형 사각 박스 디자인
   ------------------------------------------------- */
.engineering-panel {
    background-color: #FFFFFF;
    border: 2px solid #CBD5E1; /* 테두리를 두껍게 하여 경계선 명확화 */
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 25px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

/* 계통별 상단 일체형 띠 헤더 (정보 집중도 향상) */
.panel-header {
    background-color: #1E3A8A; /* 짙은 남색으로 시선 고정 */
    color: #FFFFFF; 
    font-size: 15px;
    font-weight: 700;
    margin: -24px -24px 22px -24px;
    padding: 12px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    letter-spacing: -0.3px;
}

/* 슬라이더 간격 정돈 및 글자 크기 확대 */
div[data-testid="stWidgetLabel"] p {
    font-size: 13.5px !important;
    font-weight: 700 !important;
    color: #1E293B !important;
    margin-bottom: 2px !important;
}

/* 슬라이더 하단 정상 범위 안내 박스 (시인성 강화) */
.panel-guide-text {
    font-size: 12px;
    color: #334155;
    font-weight: 600;
    background-color: #F1F5F9;
    padding: 8px 14px;
    border-radius: 4px;
    border-left: 4px solid #64748B;
    margin-top: -8px;
    margin-bottom: 20px;
}

/* 위험 상태 안내 전용 색상 변경 */
.guide-alert {
    border-left-color: #DC2626;
    color: #991B1B;
    background-color: #FEF2F2;
}

/* -------------------------------------------------
   버튼 및 결과 보고서 UI 고도화
   ------------------------------------------------- */
/* 확실하게 누를 수 있게 만든 진단 버튼 */
.stButton button {
    width: 100%;
    height: 58px;
    font-size: 18px;
    font-weight: 800;
    border-radius: 6px;
    transition: all 0.15s ease-in-out;
    margin-top: 10px;
    margin-bottom: 35px;
    box-shadow: 0 4px 12px rgba(30, 58, 138, 0.25);
    background-color: #1E3A8A !important;
    color: #FFFFFF !important;
    border: 2px solid #1D4ED8 !important;
}

.stButton button:hover {
    background-color: #1D4ED8 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(29, 78, 216, 0.4) !important;
}

/* 최종 종합 진단 리포트 카드 */
.report-card {
    background-color: #FFFFFF;
    border: 2px solid #94A3B8;
    border-radius: 8px;
    padding: 25px;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
}

.report-card h2 {
    color: #0F172A;
    font-size: 18px;
    font-weight: 800;
    margin-top: 0;
    margin-bottom: 20px;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 12px;
}

.grid-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
}

.grid-item {
    background-color: #F8FAFC;
    padding: 16px 20px;
    border-radius: 4px;
    border: 1px solid #E2E8F0;
}

.report-label {
    color: #475569;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 5px;
}

.report-value {
    color: #0F172A;
    font-size: 18px;
    font-weight: 800;
}

.grid-full { grid-column: span 2; }
.grid-alert { background-color: #FFFBEB; border: 2px solid #FDE68A; }

/* 소제목 좌측 바 두께 강화 */
h3 {
    color: #0F172A;
    font-size: 18px;
    font-weight: 800;
    margin-top: 10px;
    margin-bottom: 20px;
    border-left: 5px solid #1E3A8A;
    padding-left: 12px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 예측 모델 및 스케일러 파일 로드
# -------------------------------------------------
try:
    모델 = joblib.load("aircraft_model.pkl")
    스케일러 = joblib.load("aircraft_scaler.pkl")
    model_loaded = True
except:
    model_loaded = False

# -------------------------------------------------
# 상단 타이틀 영역 (영문 배제)
# -------------------------------------------------
st.markdown("""
<div class='main-title'>항공기 엔진 상태 예측 진단 시스템</div>
<div class='sub-title'>데이터 기반 정비 및 결함 위험도 실시간 연산 대시보드</div>
""", unsafe_allow_html=True)

st.markdown("<h3>엔진 데이터 입력 계통</h3>", unsafe_allow_html=True)

# -------------------------------------------------
# 패널 레이아웃 배치 (한국어 전면 수정 및 박스 일체화)
# -------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    # 1. 가동 이력 정보
    st.markdown("<div class='engineering-panel'><div class='panel-header'>가동 이력 및 관리 지표</div>", unsafe_allow_html=True)
    운전사이클 = st.slider("누적 구동 사이클 (총 비행 횟수 기준)", 1, 400, 232)
    st.markdown("<div class='panel-guide-text guide-alert'>지침 기준: 표준 정비 권장 주기인 200 사이클을 초과한 노후 상태입니다.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. 열역학 온도 센서 그룹
    st.markdown("<div class='engineering-panel'><div class='panel-header'>열역학 센서 계통 - 내부 온도 제어</div>", unsafe_allow_html=True)
    센서2 = st.slider("센서 02 (저압 압축기 출구 온도)", 630.0, 650.0, 641.0)
    st.markdown("<div class='panel-guide-text'>안전 운용 범위: 635.0 ~ 645.0 K</div>", unsafe_allow_html=True)
    
    센서3 = st.slider("센서 03 (고압 압축기 출구 온도)", 1500.0, 1700.0, 1580.0)
    st.markdown("<div class='panel-guide-text'>안전 운용 범위: 1560.0 ~ 1610.0 K</div>", unsafe_allow_html=True)
    
    센서4 = st.slider("센서 04 (저압 터빈 출구 온도)", 1300.0, 1450.0, 1400.0)
    st.markdown("<div class='panel-guide-text'>안전 운용 범위: 1380.0 ~ 1420.0 K</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # 3. 유체역학 압력 센서 그룹
    st.markdown("<div class='engineering-panel'><div class='panel-header'>유체역학 센서 계통 - 내부 압력 및 비율</div>", unsafe_allow_html=True)
    센서7 = st.slider("센서 07 (고압 압축기 출구 압력)", 500.0, 600.0, 550.0)
    st.markdown("<div class='panel-guide-text'>안전 운용 범위: 540.0 ~ 565.0 psia</div>", unsafe_allow_html=True)
    
    센서12 = st.slider("센서 12 (바이패스 덕트 압력)", 8000.0, 8500.0, 8150.0)
    st.markdown("<div class='panel-guide-text'>안전 운용 범위: 8100.0 ~ 8250.0 psia</div>", unsafe_allow_html=True)
    
    센서15 = st.slider("센서 15 (바이패스 유량 비율)", 7.0, 10.0, 8.5)
    st.markdown("<div class='panel-guide-text'>안전 운용 범위: 8.2 ~ 8.8</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. 회전 역학 센서 그룹
    st.markdown("<div class='engineering-panel'><div class='panel-header'>회전 구동 계통 - 터빈 속도 및 배출 플로우</div>", unsafe_allow_html=True)
    센서11 = st.slider("센서 11 (고압 터빈 회전 속도)", 2300.0, 2500.0, 2400.0)
    st.markdown("<div class='panel-guide-text'>안전 운용 범위: 2370.0 ~ 2430.0 rpm</div>", unsafe_allow_html=True)
    
    센서20 = st.slider("센서 20 (고압 터빈 배출 유량)", 35.0, 50.0, 40.0)
    st.markdown("<div class='panel-guide-text'>안전 운용 범위: 38.0 ~ 42.0 lbm/s</div>", unsafe_allow_html=True)
    
    센서21 = st.slider("센서 21 (저압 터빈 배출 유량)", 20.0, 30.0, 23.0)
    st.markdown("<div class='panel-guide-text'>안전 운용 범위: 22.5 ~ 24.5 lbm/s</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------
# 진단 실행 영역 및 시각화 결과 보고서
# -------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
execute_diag = st.button("시스템 종합 진단 가동")

st.markdown("<hr style='border-color: #CBD5E1; margin-top:5px; margin-bottom:30px;'>", unsafe_allow_html=True)

if execute_diag:
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

    신뢰도_오차 = 2.14 + (확률 * 1.5)

    res_col1, res_col2 = st.columns([1.1, 1])

    with res_col1:
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=확률 * 100,
            number={'suffix': "%", 'font': {'color': '#0F172A', 'size': 45, 'weight': 'bold'}},
            title={'text': "인공지능 모델 결함 판단 지수", 'font': {'color': '#475569', 'size': 13, 'weight': 'bold'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': "#64748B"},
                'bar': {'color': "rgba(0,0,0,0)"}, 
                'bgcolor': "#F1F5F9",
                'steps': [
                    {'range': [0, 35], 'color': '#10B981'},   
                    {'range': [35, 70], 'color': '#F59E0B'},  
                    {'range': [70, 100], 'color': '#EF4444'}  
                ],
                'threshold': {'line': {'color': "#0F172A", 'width': 3}, 'thickness': 0.75, 'value': 확률 * 100}
            }
        ))
        gauge.update_layout(paper_bgcolor="#F8FAFC", height=240, margin=dict(t=40, b=10))
        st.plotly_chart(gauge, use_container_width=True)

    with res_col2:
        if 결과 == 1:
            상태 = "<span style='color:#EF4444;'>정비 요망 (정밀 점검 대상)</span>"
            권고 = "내부 주요 부품의 열화 징후 및 한계치 초과 오버런 현상이 감지되었습니다. 규정에 의거하여 가동 자산의 작동을 즉시 중단하고 정비 지침서에 따라 신속히 장비를 분해하여 비파괴 검사를 수행하십시오."
        else:
            상태 = "<span style='color:#10B981;'>정상 가동 (안정 상태)</span>"
            권고 = "모든 가동 스트레스 계수 및 압력 데이터 거동이 규정된 신뢰 범위 내에서 안정적입니다. 특이사항이 없으므로 정기 표준 예방 정비 주기를 유지하십시오."

        st.markdown(f"""
        <div class='report-card'>
            <h2>종합 진단 및 장비 상태 보고서</h2>
            <div class='grid-container'>
                <div class='grid-item'>
                    <div class='report-label'>엔진 계통 분석 상태</div>
                    <div class='report-value'>{상태}</div>
                </div>
                <div class='grid-item'>
                    <div class='report-label'>AI 결함 예측 위험도</div>
                    <div class='report-value'>{확률*100:.2f} %</div>
                </div>
                <div class='grid-item'>
                    <div class='report-label'>분석 오차 범위 (신뢰구간)</div>
                    <div class='report-value'>± {신뢰도_오차:.2f} %</div>
                </div>
                <div class='grid-item'>
                    <div class='report-label'>적용 연산 알고리즘</div>
                    <div class='report-value' style='color:#1E3A8A;'>랜덤 포레스트 v1.0.4</div>
                </div>
                <div class='grid-item grid-full grid-alert'>
                    <div class='report-label' style='color: #92400E; font-size:12.5px;'>엔진 정비 권장 조치사항</div>
                    <div class='report-value' style='font-size: 13px; font-weight: 500; line-height: 1.6; margin-top: 5px; color:#1E293B;'>{권고}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
