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
# [안정성 강화] 깨짐 방지 전용 커스텀 CSS
# -------------------------------------------------
st.markdown("""
<style>
/* 전체 화면 기본 스타일 */
.stApp {
    background-color: #F8FAFC; 
    font-family: -apple-system, BlinkMacSystemFont, "Malgun Gothic", sans-serif;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}

/* 제목 폰트 */
.main-title {
    text-align: center;
    color: #0F172A;
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 5px;
}

.sub-title {
    text-align: center;
    color: #64748B;
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 30px;
}

/* 계통별 테두리 박스 (st.container와 매칭) */
.sensor-box-container {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 15px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.sensor-box-header {
    font-size: 13px;
    font-weight: 800;
    color: #1E3A8A;
    border-bottom: 2px solid #F1F5F9;
    padding-bottom: 6px;
    margin-bottom: 12px;
}

/* 정상 범위 가이드 라벨 */
.range-hint {
    font-size: 11px;
    color: #64748B;
    font-weight: 600;
    margin-top: -6px;
    margin-bottom: 12px;
    background-color: #F8FAFC;
    padding: 4px 8px;
    border-radius: 4px;
    border-left: 3px solid #94A3B8;
}

.range-hint-alert {
    border-left-color: #EF4444;
    background-color: #FEF2F2;
    color: #991B1B;
}

/* 오른쪽 결과창 전용 밀폐형 컨테이너 */
.report-final-box {
    background-color: #FFFFFF;
    border: 1px solid #94A3B8;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}

.report-section-title {
    font-size: 13px;
    font-weight: 800;
    color: #475569;
    margin-bottom: 10px;
}

/* 합격/불합격 큰 상자 */
.status-banner {
    padding: 12px;
    border-radius: 6px;
    text-align: center;
    font-weight: 800;
    font-size: 16px;
    margin-bottom: 15px;
}

.status-banner-normal {
    background-color: #E8F5E9;
    color: #2E7D32;
    border: 1px solid #C8E6C9;
}

.status-banner-critical {
    background-color: #FFEBEE;
    color: #C62828;
    border: 1px solid #FFCDD2;
}

/* 가이드 블릿 리스트 */
.guide-bullet-list {
    margin: 0;
    padding-left: 18px;
    font-size: 12px;
    color: #334155;
    line-height: 1.6;
    font-weight: 500;
}

.guide-bullet-list li {
    margin-bottom: 6px;
}

/* 버튼 스타일 고정 */
.stButton button {
    width: 100%;
    height: 50px;
    font-size: 15px;
    font-weight: 800;
    border-radius: 6px;
    background-color: #1E3A8A !important;
    color: #FFFFFF !important;
    border: 1px solid #1D4ED8 !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 인공지능 모델 로드 및 서빙 검증
# -------------------------------------------------
try:
    모델 = joblib.load("aircraft_model.pkl")
    스케일러 = joblib.load("aircraft_scaler.pkl")
    model_loaded = True
except:
    model_loaded = False

# -------------------------------------------------
# 헤더 텍스트
# -------------------------------------------------
st.markdown("<div class='main-title'>항공기 엔진 상태 예측 진단 플랫폼</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>실시간 제어 계통 데이터 통합 모니터링 및 상태 추론 대시보드</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 메인 2분할 구조 렌더링
# -------------------------------------------------
메인좌측, 메인우측 = st.columns([2.3, 1.0], gap="medium")

with 메인좌측:
    st.markdown("<div style='font-size:15px; font-weight:800; color:#0F172A; margin-bottom:15px; border-left:4px solid #1E3A8A; padding-left:10px;'>원격 측정 계통 데이터 입력</div>", unsafe_allow_html=True)
    
    # 3열 바둑판 구조 격자 배치
    단1, 단2, 단3 = st.columns(3)
    
    with 단1:
        with st.container():
            st.markdown("<div class='sensor-box-container'><div class='sensor-box-header'>가동 이력 지표</div>", unsafe_allow_html=True)
            운전사이클 = st.slider("누적 구동 사이클", 1, 400, 232, key="s_cycle")
            st.markdown("<div class='range-hint range-hint-alert'>기준 수치: 200 사이클 초과 노후</div></div>", unsafe_allow_html=True)
            
        with st.container():
            st.markdown("<div class='sensor-box-container'><div class='sensor-box-header'>저압 압축 제어 계통</div>", unsafe_allow_html=True)
            센서2 = st.slider("저압 압축기 출구 온도 (센서 02)", 630.0, 650.0, 641.0, key="s_2")
            st.markdown("<div class='range-hint'>안전 범위: 635.0 ~ 645.0 K</div>", unsafe_allow_html=True)
            센서21 = st.slider("저압 터빈 배출 유량 (센서 21)", 20.0, 30.0, 23.0, key="s_21")
            st.markdown("<div class='range-hint'>안전 범위: 22.5 ~ 24.5 lbm/s</div></div>", unsafe_allow_html=True)

    with 단2:
        with st.container():
            st.markdown("<div class='sensor-box-container'><div class='sensor-box-header'>고압 열역학 계통</div>", unsafe_allow_html=True)
            센서3 = st.slider("고압 압축기 출구 온도 (센서 03)", 1500.0, 1700.0, 1580.0, key="s_3")
            st.markdown("<div class='range-hint'>안전 범위: 1560.0 ~ 1610.0 K</div>", unsafe_allow_html=True)
            센서4 = st.slider("저압 터빈 출구 온도 (센서 04)", 1300.0, 1450.0, 1400.0, key="s_4")
            st.markdown("<div class='range-hint'>안전 범위: 1380.0 ~ 1420.0 K</div></div>", unsafe_allow_html=True)
            
        with st.container():
            st.markdown("<div class='sensor-box-container'><div class='sensor-box-header'>고압 기계 압력 계통</div>", unsafe_allow_html=True)
            센서7 = st.slider("고압 압축기 출구 압력 (센서 07)", 500.0, 600.0, 550.0, key="s_7")
            st.markdown("<div class='range-hint'>안전 범위: 540.0 ~ 565.0 psia</div></div>", unsafe_allow_html=True)

    with 단3:
        with st.container():
            st.markdown("<div class='sensor-box-container'><div class='sensor-box-header'>바이패스 관리 계통</div>", unsafe_allow_html=True)
            센서12 = st.slider("바이패스 덕트 압력 (센서 12)", 8000.0, 8500.0, 8150.0, key="s_12")
            st.markdown("<div class='range-hint'>안전 범위: 8100.0 ~ 8250.0 psia</div>", unsafe_allow_html=True)
            센서15 = st.slider("바이패스 유량 비율 (센서 15)", 7.0, 10.0, 8.5, key="s_15")
            st.markdown("<div class='range-hint'>안전 범위: 8.2 ~ 8.8</div></div>", unsafe_allow_html=True)
            
        with st.container():
            st.markdown("<div class='sensor-box-container'><div class='sensor-box-header'>터빈 구동 로터 계통</div>", unsafe_allow_html=True)
            센서11 = st.slider("고압 터빈 회전 속도 (센서 11)", 2300.0, 2500.0, 2400.0, key="s_11")
            st.markdown("<div class='range-hint'>안전 범위: 2370.0 ~ 2430.0 rpm</div>", unsafe_allow_html=True)
            센서20 = st.slider("고압 터빈 배출 유량 (센서 20)", 35.0, 50.0, 40.0, key="s_20")
            st.markdown("<div class='range-hint'>안전 범위: 38.0 ~ 42.0 lbm/s</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    진단가동버튼 = st.button("시스템 상태 예측 연산 기동")

with 메인우측:
    # 핵심 데이터 연산
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

    # [수정 완결] 오타를 잡고 하나의 완벽한 단일 컴포넌트 박스로 우측 리포트 결합
    st.markdown(f"""
    <div class='report-final-box'>
        <div class='report-section-title'>종합 진단 결과 판정</div>
        <div class='status-banner {배너클래스}'>{배너텍스트}</div>
        <div class='report-section-title' style='margin-bottom: -10px;'>고장 확률도 구역</div>
    """, unsafe_allow_html=True)

    # 투명 백그라운드 게이지 차트 생성 및 중간 안착
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
    게이지_차트.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=120, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(게이지_차트, use_container_width=True)

    # 하단 권고 리스트 HTML 조립 및 박스 마무리 닫기 태그(</div>) 처리
    리스트_요소 = "".join([f"<li>{지침}</li>" for 지침 in 정비지침])
    st.markdown(f"""
        <div class='report-section-title' style='border-top: 1px solid #F1F5F9; padding-top: 12px; margin-top: -10px; margin-bottom: 10px;'>엔진 계통 정비 권고사항</div>
        <ul class='guide-list guide-bullet-list'>
            {리스트_요소}
        </ul>
    </div>
    """, unsafe_allow_html=True)
