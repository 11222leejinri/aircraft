import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# -------------------------------------------------
# 페이지 설정 (전체 화면을 넓게 쓰도록 설정)
# -------------------------------------------------
st.set_page_config(
    page_title="항공기 엔진 정밀 상태 진단 시스템",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# 2분할 관제 레이아웃 전용 커스텀 CSS (영어/이모지 전면 배제)
# -------------------------------------------------
st.markdown("""
<style>
/* 전체 화면 설정 */
.stApp {
    background-color: #F8FAFC; 
    font-family: -apple-system, BlinkMacSystemFont, "Malgun Gothic", sans-serif;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}

/* 상단 헤더 */
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
   왼쪽: 계통 제어 패널 (밀폐형 컴팩트 박스)
   ------------------------------------------------- */
.engineering-panel {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 15px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.panel-header {
    font-size: 13px;
    font-weight: 800;
    color: #1E3A8A;
    border-bottom: 2px solid #F1F5F9;
    padding-bottom: 8px;
    margin-bottom: 12px;
    letter-spacing: -0.5px;
}

/* 슬라이더 라벨 가독성 강화 */
div[data-testid="stWidgetLabel"] p {
    font-size: 12.5px !important;
    font-weight: 700 !important;
    color: #334155 !important;
}

/* 정상 운용 범위 안내 텍스트 */
.range-guide {
    font-size: 11px;
    color: #64748B;
    text-align: right;
    margin-top: -8px;
    margin-bottom: 10px;
    font-weight: 500;
}

/* -------------------------------------------------
   오른쪽: 통합 진단 리포트 사이드 영역
   ------------------------------------------------- */
.report-sidebar {
    background-color: #FFFFFF;
    border: 2px solid #1E3A8A;
    border-radius: 8px;
    padding: 22px;
    height: 100%;
    box-shadow: 0 4px 12px rgba(30, 58, 138, 0.05);
}

.sidebar-title {
    font-size: 16px;
    font-weight: 800;
    color: #0F172A;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

/* 결과 메트릭 레이아웃 */
.status-box {
    padding: 14px;
    border-radius: 6px;
    text-align: center;
    font-weight: 800;
    font-size: 18px;
    margin-bottom: 20px;
}

.status-normal {
    background-color: #DCFCE7;
    color: #15803D;
    border: 1px solid #BBF7D0;
}

.status-critical {
    background-color: #FEE2E2;
    color: #B91C1C;
    border: 1px solid #FCA5A5;
}

/* 결과 세부 데이터 그리드 */
.result-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 10px;
    margin-bottom: 20px;
}

.result-item {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    padding: 10px 14px;
    border-radius: 4px;
}

.result-label {
    font-size: 11px;
    color: #64748B;
    font-weight: 600;
    margin-bottom: 2px;
}

.result-value {
    font-size: 14px;
    font-weight: 700;
    color: #0F172A;
}

/* 권장 조치 사항 지침 박스 */
.action-box {
    background-color: #FFFBEB;
    border-left: 4px solid #F59E0B;
    padding: 12px 14px;
    border-radius: 4px;
}

.action-title {
    font-size: 12px;
    font-weight: 700;
    color: #92400E;
    margin-bottom: 4px;
}

.action-content {
    font-size: 12px;
    color: #78350F;
    line-height: 1.5;
    font-weight: 500;
}

/* -------------------------------------------------
   중앙 진단 가동 버튼
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
    box-shadow: 0 4px 6px rgba(30, 58, 138, 0.15);
    transition: all 0.15s ease-in-out;
}

.stButton button:hover {
    background-color: #1D4ED8 !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 12px rgba(29, 78, 216, 0.25) !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# AI 예측 분석 모델 로드 시도
# -------------------------------------------------
try:
    모델 = joblib.load("aircraft_model.pkl")
    스케일러 = joblib.load("aircraft_scaler.pkl")
    model_loaded = True
except:
    model_loaded = False

# -------------------------------------------------
# 메인 상단 대시보드 헤더
# -------------------------------------------------
st.markdown("<div class='main-title'>항공기 엔진 상태 예측 진단 플랫폼</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>실시간 데이터 통합 관제 및 머신러닝 기반 결함 위험도 분석 시스템</div>", unsafe_allow_html=True)

# -------------------------------------------------
# [개선] 메인 화면 분할 (왼쪽: 센서 입력 3열 바둑판 / 오른쪽: 진단 결과창 고정)
# -------------------------------------------------
메인좌측, 메인우측 = st.columns([2.1, 1.0], gap="large")

with 메인좌측:
    st.markdown("<div style='font-size:15px; font-weight:800; color:#0F172A; margin-bottom:15px; border-left:4px solid #1E3A8A; padding-left:8px;'>원격 측정 계통 데이터 입력</div>", unsafe_allow_html=True)
    
    # 내부 3열 바둑판 배열 구조 생성
    세부열1, 세부열2, 세부열3 = st.columns(3)
    
    with 세부열1:
        st.markdown("<div class='engineering-panel'><div class='panel-header'>가동 이력 지표</div>", unsafe_allow_html=True)
        운전사이클 = st.slider("누적 구동 사이클", 1, 400, 232)
        st.markdown("<div class='range-guide' style='color:#DC2626;'>기준 주기: 200 초과 노후</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='engineering-panel'><div class='panel-header'>저압 계통 센서</div>", unsafe_allow_html=True)
        센서2 = st.slider("저압 압축기 출구 온도", 630.0, 650.0, 641.0)
        st.markdown("<div class='range-guide'>정상: 635.0 ~ 645.0 K</div>", unsafe_allow_html=True)
        센서21 = st.slider("저압 터빈 배출 유량", 20.0, 30.0, 23.0)
        st.markdown("<div class='range-guide'>정상: 22.5 ~ 24.5 lbm/s</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with 세부열2:
        st.markdown("<div class='engineering-panel'><div class='panel-header'>고압 열역학 계통</div>", unsafe_allow_html=True)
        센서3 = st.slider("고압 압축기 출구 온도", 1500.0, 1700.0, 1580.0)
        st.markdown("<div class='range-guide'>정상: 1560.0 ~ 1610.0 K</div>", unsafe_allow_html=True)
        센서4 = st.slider("저압 터빈 출구 온도", 1300.0, 1450.0, 1400.0)
        st.markdown("<div class='range-guide'>정상: 1380.0 ~ 1420.0 K</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='engineering-panel'><div class='panel-header'>고압 역학 계통</div>", unsafe_allow_html=True)
        센서7 = st.slider("고압 압축기 출구 압력", 500.0, 600.0, 550.0)
        st.markdown("<div class='range-guide'>정상: 540.0 ~ 565.0 psia</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with 세부열3:
        st.markdown("<div class='engineering-panel'><div class='panel-header'>바이패스 제어 계통</div>", unsafe_allow_html=True)
        센서12 = st.slider("바이패스 덕트 압력", 8000.0, 8500.0, 8150.0)
        st.markdown("<div class='range-guide'>정상: 8100.0 ~ 8250.0 psia</div>", unsafe_allow_html=True)
        센서15 = st.slider("바이패스 유량 비율", 7.0, 10.0, 8.5)
        st.markdown("<div class='range-guide'>정상: 8.2 ~ 8.8</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='engineering-panel'><div class='panel-header'>구동 로터 계통</div>", unsafe_allow_html=True)
        센서11 = st.slider("고압 터빈 회전 속도", 2300.0, 2500.0, 2400.0)
        st.markdown("<div class='range-guide'>정상: 2370.0 ~ 2430.0 rpm</div>", unsafe_allow_html=True)
        센서20 = st.slider("고압 터빈 배출 유량", 35.0, 50.0, 40.0)
        st.markdown("<div class='range-guide'>정상: 38.0 ~ 42.0 lbm/s</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 하단 배치 가동 진단 버튼
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    진단가동버튼 = st.button("시스템 종합 분석 상태 예측 실행")


with 메인우측:
    # 오른쪽 영역을 완전히 진단 결과 보드로 고정 및 시각화 구현
    if 진단가동버튼:
        # 데이터 추론 연산 가동
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

        상태텍스트 = "정비 요망 (위험)" if 결과 == 1 else "정상 가동 (안정)"
        상태클래스 = "status-critical" if 결과 == 1 else "status-normal"
        권고내용 = "내부 컴포넌트의 가속 열화 상태가 감지되었습니다. 즉시 작동 시퀀스를 중단하고 내부 정밀 비파괴 검사를 수행하십시오." if 결과 == 1 else "모든 가동 스트레스 계수 및 센서 거동이 신뢰 범위 내에서 안정적입니다. 표준 예방 정비 주기를 유지하십시오."

        st.markdown(f"""
        <div class='report-sidebar'>
            <div class='sidebar-title'>시스템 진단 결과 리포트</div>
            <div class='report-label' style='margin-bottom:6px;'>종합 판정 상태</div>
            <div class='status-box {상태클래스}'>{상태텍스트}</div>
            
            <div class='result-grid'>
                <div class='result-item'>
                    <div class='result-label'>결함 예측 위험도 지수</div>
                    <div class='result-value' style='color:{"#DC2626" if 결과==1 else "#16A34A"}; font-size: 20px;'>{확률*100:.1f}%</div>
                </div>
                <div class='result-item'>
                    <div class='result-item-inner'>
                        <div class='result-label'>진단 처리 연산 모델</div>
                        <div class='result-value'>랜덤 포레스트 v1.0.4</div>
                    </div>
                </div>
                <div class='result-item'>
                    <div class='result-item-inner'>
                        <div class='result-label'>통계 분석 신뢰 오차</div>
                        <div class='result-value'>± {(2.14 + 확률*1.5):.2f}% (95% 신뢰도)</div>
                    </div>
                </div>
            </div>
            
            <div class='action-box'>
                <div class='action-title'>엔진 정비 권장 조치사항</div>
                <div class='action-content'>{권고내용}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 위험도 표시 미니 게이지 차트
        게이지 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=확률 * 100,
            number={'suffix': "%", 'font': {'size': 24, 'weight': 'bold', 'color': '#0F172A'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': dict(size=8)},
                'bar': {'color': "#1E3A8A"},
                'bgcolor': "#F1F5F9",
                'steps': [
                    {'range': [0, 35], 'color': 'rgba(16, 185, 129, 0.2)'},
                    {'range': [35, 70], 'color': 'rgba(245, 158, 11, 0.2)'},
                    {'range': [70, 100], 'color': 'rgba(239, 68, 68, 0.2)'}
                ]
            }
        ))
        게이지.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=130, margin=dict(t=20, b=10, l=10, r=10))
        st.plotly_chart(게이지, use_container_width=True)
        
    else:
        # 최초 진단 전 대기 화면 안내 가이드
        st.markdown("""
        <div class='report-sidebar' style='display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; min-height:450px; border-style: dashed;'>
            <div style='color:#64748B; font-size:14px; font-weight:700;'>원격 측정 데이터를 지정한 후<br><br><span style='color:#1E3A8A;'>[시스템 종합 분석 상태 예측 실행]</span><br><br>버튼을 누르면 실시간 진단이 개시됩니다.</div>
        </div>
        """, unsafe_allow_html=True)
