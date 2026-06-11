import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# -------------------------------------------------
# 페이지 설정 (사이드바 제거, 전체 화면 제어)
# -------------------------------------------------
st.set_page_config(
    page_title="항공기 엔진 정밀 상태 진단 시스템",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# 대시보드 전용 계측기 스타일 CSS (영어/이모지 전면 제거)
# -------------------------------------------------
st.markdown("""
<style>
/* 전체 배경 및 기본 서체 정의 */
.stApp {
    background-color: #F8FAFC; 
    font-family: -apple-system, BlinkMacSystemFont, "Malgun Gothic", sans-serif;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}

/* 상단 타이틀 구조 */
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

/* -------------------------------------------------
   [구조 개혁] 슬라이더와 가이드를 하나로 묶는 계측기 카드
   ------------------------------------------------- */
.sensor-block {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 14px 18px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

/* 카드 상단 헤더 밴드 */
.sensor-block-header {
    font-size: 13px;
    font-weight: 800;
    color: #1E3A8A;
    border-bottom: 2px solid #F1F5F9;
    padding-bottom: 6px;
    margin-bottom: 12px;
}

/* 데이터 가이드 및 수치 범위 범례 */
.sensor-meta-grid {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #64748B;
    font-weight: 600;
    margin-top: -6px;
    background-color: #F8FAFC;
    padding: 4px 8px;
    border-radius: 4px;
}

/* Streamlit 기본 슬라이더 라벨 크기 축소 및 일체화 */
div[data-testid="stWidgetLabel"] p {
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #1E293B !important;
}

/* -------------------------------------------------
   오른쪽: 시안과 완벽 매칭된 직관적 결과 사이드바
   ------------------------------------------------- */
.result-sidebar {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

/* 최상단 큰 알림판 스타일 */
.status-banner {
    padding: 12px;
    border-radius: 6px;
    text-align: center;
    font-weight: 800;
    font-size: 16px;
    margin-bottom: 18px;
    letter-spacing: -0.3px;
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

/* 리포트 섹션 소제목 */
.report-section-title {
    font-size: 13px;
    font-weight: 700;
    color: #475569;
    margin-bottom: 8px;
}

/* 하단 권고사항 목록 레이아웃 */
.instruction-list {
    margin: 0;
    padding-left: 18px;
    font-size: 12px;
    color: #334155;
    line-height: 1.6;
    font-weight: 500;
}

.instruction-list li {
    margin-bottom: 6px;
}

/* -------------------------------------------------
   예측 실행 버튼 리디자인
   ------------------------------------------------- */
.stButton button {
    width: 100%;
    height: 50px;
    font-size: 15px;
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
# 데이터 분석 핵심 모델 로드
# -------------------------------------------------
try:
    모델 = joblib.load("aircraft_model.pkl")
    스케일러 = joblib.load("aircraft_scaler.pkl")
    model_loaded = True
except:
    model_loaded = False

# -------------------------------------------------
# 대시보드 최상단 타이틀
# -------------------------------------------------
st.markdown("<div class='main-title'>항공기 엔진 상태 예측 진단 플랫폼</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>실시간 제어 계통 데이터 통합 모니터링 및 상태 추론 보드</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 좌측 계측기 바둑판(Grid) 영역 및 우측 결과창 2분할 구성
# -------------------------------------------------
레이아웃좌측, 레이아웃우측 = st.columns([2.2, 1.0], gap="medium")

with 레이아웃좌측:
    # 3열 바둑판 구조 격자 생성
    단단1, 단단2, 단단3 = st.columns(3)
    
    with 단단1:
        st.markdown("<div class='sensor-block'><div class='sensor-block-header'>가동 지표 정보</div>", unsafe_allow_html=True)
        운전사이클 = st.slider("누적 구동 사이클", 1, 400, 232)
        st.markdown("<div class='sensor-meta-grid'><span>정비 기준: 200 사이클</span><span style='color:#DC2626;'>노후 상태</span></div></div>", unsafe_allow_html=True)

        st.markdown("<div class='sensor-block'><div class='sensor-block-header'>저압 압축 제어 계통</div>", unsafe_allow_html=True)
        센서2 = st.slider("저압 압축기 출구 온도", 630.0, 650.0, 641.0)
        st.markdown("<div class='sensor-meta-grid'><span>하한: 635.0 K</span><span>상한: 645.0 K</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with 단단2:
        st.markdown("<div class='sensor-block'><div class='sensor-block-header'>고압 열역학 계통</div>", unsafe_allow_html=True)
        센서3 = st.slider("고압 압축기 출구 온도", 1500.0, 1700.0, 1580.0)
        st.markdown("<div class='sensor-meta-grid'><span>하한: 1560.0 K</span><span>상한: 1610.0 K</span></div>", unsafe_allow_html=True)
        
        센서4 = st.slider("저압 터빈 출구 온도", 1300.0, 1450.0, 1400.0)
        st.markdown("<div class='sensor-meta-grid'><span>하한: 1380.0 K</span><span>상한: 1420.0 K</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='sensor-block'><div class='sensor-block-header'>고압 기계 압력 계통</div>", unsafe_allow_html=True)
        센서7 = st.slider("고압 압축기 출구 압력", 500.0, 600.0, 550.0)
        st.markdown("<div class='sensor-meta-grid'><span>하한: 540.0 psia</span><span>상한: 565.0 psia</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with 단단3:
        st.markdown("<div class='sensor-block'><div class='sensor-block-header'>바이패스 관리 계통</div>", unsafe_allow_html=True)
        센서12 = st.slider("바이패스 덕트 압력", 8000.0, 8500.0, 8150.0)
        st.markdown("<div class='sensor-meta-grid'><span>하한: 8100.0 psia</span><span>상한: 8250.0 psia</span></div>", unsafe_allow_html=True)
        
        센서15 = st.slider("바이패스 유량 비율", 7.0, 10.0, 8.5)
        st.markdown("<div class='sensor-meta-grid'><span>하한: 8.2</span><span>상한: 8.8</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='sensor-block'><div class='sensor-block-header'>터빈 구동 로터 계통</div>", unsafe_allow_html=True)
        센서11 = st.slider("고압 터빈 회전 속도", 2300.0, 2500.0, 2400.0)
        st.markdown("<div class='sensor-meta-grid'><span>하한: 2370.0 rpm</span><span>상한: 2430.0 rpm</span></div>", unsafe_allow_html=True)
        
        센서20 = st.slider("고압 터빈 배출 유량", 35.0, 50.0, 40.0)
        st.markdown("<div class='sensor-meta-grid'><span>하한: 38.0 lbm/s</span><span>상한: 42.0 lbm/s</span></div>", unsafe_allow_html=True)
        
        센서21 = st.slider("저압 터빈 배출 유량", 20.0, 30.0, 23.0)
        st.markdown("<div class='sensor-meta-grid'><span>하한: 22.5 lbm/s</span><span>상한: 24.5 lbm/s</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    진단가동버튼 = st.button("상태 예측 및 연산 가동")

with  레이아웃우측:
    # 데이터 연산 처리 부
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

    # 결과 판정 스위칭 데이터 정의
    if 결과 == 1:
        배너텍스트, 배너클래스 = "정비 권고 대상 (불합격)", "status-banner-critical"
        리포트_리스트 = [
            "내부 컴포넌트의 가속 열화 상태가 수치상 확인되었습니다.",
            "즉시 엔진 시퀀스 작동을 차단 조치하십시오.",
            "정비 지침서에 의거하여 정밀 비파괴 검사를 수행하십시오."
        ]
    else:
        배너텍스트, 배너클래스 = "안정 가동 상태 (합격)", "status-banner-normal"
        리포트_리스트 = [
            "모든 가동 스트레스 계수가 신뢰 한계 구역 내에 있습니다.",
            "특이 징후가 발견되지 않은 정상 데이터 범주입니다.",
            "기존에 계획된 표준 예방 정비 주기를 유지하십시오."
        ]

    # 시안과 동일한 우측 레이아웃 설계안 적용
    st.markdown(f"""
    <div class='result-sidebar'>
        <div class='report-section-title'>시스템 진단 결과</div>
        <div class='status-banner {배너클래스}'>{배너텍스트}</div>
        
        <div class='report-section-title' style='margin-top:20px; margin-bottom:5px;'>고장 확률도</div>
    </div>
    """, unsafe_allow_html=True)

    # 고장 확률 미니 게이지 차트 (박스 중간 삽입)
    게이지 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=확률 * 100,
        number={'suffix': "%", 'font': {'size': 26, 'weight': 'bold', 'color': '#0F172A'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#64748B", 'tickfont': dict(size=8)},
            'bar': {'color': "#1E3A8A"},
            'bgcolor': "#F1F5F9",
            'steps': [
                {'range': [0, 35], 'color': 'rgba(16, 185, 129, 0.15)'},
                {'range': [35, 70], 'color': 'rgba(245, 158, 11, 0.15)'},
                {'range': [70, 100], 'color': 'rgba(239, 68, 68, 0.15)'}
            ]
        }
    ))
    게이지.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=120, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(게이지, use_container_width=True)

    # 하단 권고 조치 사항 리스트 출력
    리스트_html = "".join([f"<li>{요소}</li>" for 요소 in 리포트_리스트])
    st.markdown(f"""
    <div class='result-sidebar' style='border-top:none; border-top-left-radius:0; border-top-right-radius:0; margin-top:-24px;'>
        <div class='report-section-title' style='border-top: 1px solid #E2E8F0; padding-top:15px;'>정비 권고 사항</div>
        <ul class='instruction-list'>
            {리스트_html}
        </ul>
    </div>
    """, unsafe_allow_html=True)
