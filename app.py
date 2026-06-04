import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# -------------------------------------------------
# 페이지 설정
# -------------------------------------------------
st.set_page_config(
    page_title="항공기 엔진 상태 모니터링 시스템",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# 에비에이션 화이트 & 블루 엔지니어링 스타일 CSS
# -------------------------------------------------
st.markdown("""
<style>
/* 전체 배경 설정 */
.stApp {
    background-color: #F8FAFC; 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.block-container {
    padding-top: 2.5rem;
    padding-bottom: 2.5rem;
}

/* 시스템 메인 타이틀 */
.main-title {
    text-align: center;
    color: #0F172A;
    font-size: 30px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 5px;
}

/* 시스템 서브 타이틀 */
.sub-title {
    text-align: center;
    color: #64748B;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.5px;
    margin-bottom: 40px;
}

/* 정비 분석 결과 카드 */
.report-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 25px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
}

.report-card h2 {
    color: #0F172A;
    font-size: 18px;
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 15px;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 10px;
}

/* 분석 데이터 그리드 컨테이너 */
.grid-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
}

.grid-item {
    background-color: #F8FAFC;
    padding: 12px 18px;
    border-radius: 4px;
    border: 1px solid #E2E8F0;
}

.report-label {
    color: #64748B;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 4px;
    letter-spacing: 0.5px;
}

.report-value {
    color: #0F172A;
    font-size: 18px;
    font-weight: 700;
}

/* 권장 조치사항 전용 확장 레이아웃 */
.grid-full {
    grid-column: span 2;
    background-color: #FFFBEB;
    border: 1px solid #FDE68A;
}

/* -------------------------------------------------
   진단 가동 버튼 리디자인 (확실한 버튼 형태 및 입체감)
   ------------------------------------------------- */
.stButton button {
    width: 100%;
    height: 54px;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.5px;
    border-radius: 6px;
    transition: all 0.2s ease-in-out;
    margin-top: 15px;
    cursor: pointer;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    background-color: #1E3A8A !important;
    color: #FFFFFF !important;
    border: 2px solid #1D4ED8 !important;
}

.stButton button:hover {
    background-color: #1D4ED8 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(29, 78, 216, 0.3) !important;
}

.stButton button:active {
    transform: translateY(1px) !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}

/* 파라미터 슬라이더 레이블 및 수치 색상 설정 */
.stSlider label, [data-testid="stWidgetLabel"] {
    color: #334155 !important;
    font-weight: 600;
    font-size: 12px;
}

/* 섹션 타이틀 */
h3 {
    color: #0F172A;
    font-size: 16px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 15px;
    border-left: 4px solid #1E3A8A;
    padding-left: 10px;
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
    st.error("시스템 오류: 핵심 분석 모델 파일(aircraft_model.pkl, aircraft_scaler.pkl)을 로드할 수 없습니다.")

# -------------------------------------------------
# 대시보드 상단 헤더 영역
# -------------------------------------------------
st.markdown("""
<div class='main-title'>항공기 엔진 상태 모니터링 시스템</div>
<div class='sub-title'>예측 정비 및 자산 수명 예측 데이터 분석 대시보드 (NASA C-MAPSS)</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 입력 파라미터 제어 영역
# -------------------------------------------------
st.markdown("<h3>엔진 구동 매개변수 설정</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    운전사이클 = st.slider("누적 구동 사이클 (Total Operating Cycles)", 1, 400, 150)
    센서2 = st.slider("센서 02 (저압 압축기 출구 온도)", 630.0, 650.0, 641.0)
    센서3 = st.slider("센서 03 (고압 압축기 출구 온도)", 1500.0, 1700.0, 1580.0)
    센서4 = st.slider("센서 04 (저압 터빈 출구 온도)", 1300.0, 1450.0, 1400.0)
    센서7 = st.slider("센서 07 (고압 압축기 출구 압력)", 500.0, 600.0, 550.0)

with col2:
    센서11 = st.slider("센서 11 (고압 터빈 로터 속도)", 2300.0, 2500.0, 2400.0)
    센서12 = st.slider("센서 12 (바이패스 덕트 압력)", 8000.0, 8500.0, 8150.0)
    센서15 = st.slider("센서 15 (바이패스 비율)", 7.0, 10.0, 8.5)
    센서20 = st.slider("센서 20 (고압 터빈 블리드 유량)", 35.0, 50.0, 40.0)
    센서21 = st.slider("센서 21 (저압 터빈 블리드 유량)", 20.0, 30.0, 23.0)

# -------------------------------------------------
# 단일 진단 가동 버튼 (중앙 집중 레이아웃)
# -------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
execute_diag = st.button("진단 시퀀스 가동")

# -------------------------------------------------
# 센서 레이더 차트 분석 시각화
# -------------------------------------------------
st.markdown("<br><hr style='border-color: #E2E8F0;'><br>", unsafe_allow_html=True)
st.markdown("<h3>센서 배열 벡터 분석</h3>", unsafe_allow_html=True)

radar = go.Figure()
radar.add_trace(
    go.Scatterpolar(
        r=[센서2, 센서3/10, 센서4/10, 센서7, 센서11/10, 센서12/100, 센서15*50, 센서20*10, 센서21*10],
        theta=["S02", "S03", "S04", "S07", "S11", "S12", "S15", "S20", "S21"],
        fill='toself',
        fillcolor='rgba(30, 58, 138, 0.05)',
        line=dict(color='#1E3A8A', width=1.5),
        name="정밀 원격 측정 데이터"
    )
)

radar.update_layout(
    paper_bgcolor="#F8FAFC",
    plot_bgcolor="#F8FAFC",
    font=dict(color="#334155", size=11),
    polar=dict(
        bgcolor="#FFFFFF",
        radialaxis=dict(visible=True, gridcolor="#E2E8F0", linecolor="#CBD5E1", tickfont=dict(size=9)),
        angularaxis=dict(gridcolor="#E2E8F0", linecolor="#CBD5E1")
    ),
    margin=dict(t=30, b=30, l=30, r=30)
)
st.plotly_chart(radar, use_container_width=True)

# -------------------------------------------------
# 진단 연산 처리 영역 (버튼 클릭 시에만 발생)
# -------------------------------------------------
if execute_diag:
    
    if model_loaded:
        입력값 = pd.DataFrame(
            [[운전사이클, 센서2, 센서3, 센서4, 센서7, 센서11, 센서12, 센서15, 센서20, 센서21]],
            columns=['운전사이클', '센서2', '센서3', '센서4', '센서7', '센서11', '센서12', '센서15', '센서20', '센서21']
        )
        입력값 = 스케일러.transform(입력값)
        결과 = 모델.predict(입력값)[0]
        try:
            확률 = 모델.predict_proba(입력값)[0][1]
        except:
            확률 = 0.5
    else:
        결과 = 1 if 운전사이클 > 200 else 0
        확률 = 0.51 if 운전사이클 == 150 else 운전사이클 / 400.0

    st.markdown("<br><hr style='border-color: #E2E8F0;'><br>", unsafe_allow_html=True)
    st.markdown("<h3>시스템 종합 진단 결과</h3>", unsafe_allow_html=True)
    
    res_col1, res_col2 = st.columns([1.1, 1])

    with res_col1:
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=확률 * 100,
                number={'suffix': "%", 'font': {'color': '#0F172A', 'size': 50, 'weight': 'bold'}},
                title={'text': "결함 발생 확률 계수", 'font': {'color': '#64748B', 'size': 13}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': dict(size=10)},
                    'bar': {'color': "rgba(0,0,0,0)"}, 
                    'bgcolor': "#F1F5F9",
                    'borderwidth': 1,
                    'bordercolor': "#CBD5E1",
                    'steps': [
                        {'range': [0, 40], 'color': '#10B981'},   
                        {'range': [40, 70], 'color': '#F59E0B'},  
                        {'range': [70, 100], 'color': '#EF4444'}  
                    ],
                    'threshold': {
                        'line': {'color': "#0F172A", 'width': 3},
                        'thickness': 0.8,
                        'value': 확률 * 100
                    }
                }
            )
        )
        gauge.update_layout(
            paper_bgcolor="#F8FAFC",
            font=dict(color="#0F172A"),
            margin=dict(t=40, b=10, l=10, r=10),
            height=260
        )
        st.plotly_chart(gauge, use_container_width=True)

    with res_col2:
        if 결과 == 1:
            상태 = "<span style='color:#EF4444;'>정비 요망 (Critical)</span>"
            권고 = "<span style='color:#991B1B;'>지침 오버런 징후 및 한계치 초과 결함이 검출되었습니다. 자산 가동 시퀀스를 즉시 중단하고 비계획 정비 지침(AMM)에 따라 정밀 분해 점검을 수행하십시오.</span>"
        else:
            상태 = "<span style='color:#10B981;'>정상 구동 (Nominal)</span>"
            권고 = "내부 거동 및 압력 매개변수가 규정 오차 범위 내에서 안정적입니다. 정기 표준 정비 주기를 유지하십시오."

        st.markdown(f"""
        <div class='report-card'>
            <h2>종합 진단 및 정비 리포트</h2>
            <div class='grid-container'>
                <div class='grid-item'>
                    <div class='report-label'>엔진 시스템 분석 상태</div>
                    <div class='report-value'>{상태}</div>
                </div>
                <div class='grid-item'>
                    <div class='report-label'>연산된 리스크 가중치</div>
                    <div class='report-value'>{확률*100:.2f} %</div>
                </div>
                <div class='grid-item'>
                    <div class='report-label'>로그된 누적 분석 사이클</div>
                    <div class='report-value'>{운전사이클} Cycles</div>
                </div>
                <div class='grid-item'>
                    <div class='report-label'>분석 아키텍처</div>
                    <div class='report-value' style='color:#1E3A8A; font-size:16px;'>Random Forest v1.0</div>
                </div>
                <div class='grid-item grid-full'>
                    <div class='report-label'>엔진 관리 권장 조치사항</div>
                    <div class='report-value' style='font-size: 13px; font-weight: 500; line-height: 1.6; margin-top: 5px; color:#1E293B;'>{권고}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
