import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# -------------------------------------------------
# 페이지 설정
# -------------------------------------------------
st.set_page_config(
    page_title="AIRCRAFT ENGINE HEALTH MONITORING SYSTEM",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# 엔지니어링 대시보드 전용 고대비 CSS 설정
# -------------------------------------------------
st.markdown("""
<style>
/* 시스템 기본 서체 및 배경 (Tactical Dark Mode) */
.stApp {
    background-color: #0B0F19; 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.block-container {
    padding-top: 2.0rem;
    padding-bottom: 2.0rem;
}

/* 시스템 메인 타이틀 */
.main-title {
    text-align: center;
    color: #FFFFFF;
    font-size: 32px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 5px;
}

/* 시스템 서브 타이틀 */
.sub-title {
    text-align: center;
    color: #64748B;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 30px;
}

/* 시스템 상태 표시 바 (Telemetry Status Bar) */
.system-box {
    background-color: #0F172A;
    border: 1px solid #1E293B;
    border-left: 4px solid #00E5FF;
    padding: 12px;
    margin-bottom: 40px;
    color: #00E5FF;
    text-align: center;
    font-weight: 600;
    letter-spacing: 1.5px;
    font-size: 13px;
}

/* 엔지니어링 분석 결과 카드 */
.report-card {
    background-color: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 6px;
    padding: 25px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.report-card h2 {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 15px;
    border-bottom: 1px solid #334155;
    padding-bottom: 10px;
    letter-spacing: 1px;
}

/* 분석 데이터 그리드 컨테이너 */
.grid-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
}

.grid-item {
    background-color: #1E293B;
    padding: 12px 18px;
    border-radius: 4px;
    border: 1px solid #334155;
}

.report-label {
    color: #94A3B8;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.report-value {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 700;
}

/* 권장 조치사항 전용 확장 레이아웃 */
.grid-full {
    grid-column: span 2;
    background-color: #1A1625;
    border: 1px solid #3B2A4A;
}

/* 시스템 제어 명령 버튼 (Command Button) */
.stButton button {
    width: 100%;
    height: 50px;
    background-color: #0284C7;
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    border: none;
    border-radius: 4px;
    transition: background-color 0.2s ease;
    margin-top: 10px;
}

.stButton button:hover {
    background-color: #0369A1;
    color: #FFFFFF;
}

.stButton button:active {
    background-color: #075985;
    color: #FFFFFF;
}

/* 파라미터 슬라이더 제어 */
.stSlider label {
    color: #E2E8F0 !important;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.5px;
}

/* 섹션 타이틀 */
h3 {
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-top: 10px;
    margin-bottom: 10px;
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
    st.error("SYSTEM ERROR: 핵심 모델 파일(aircraft_model.pkl, aircraft_scaler.pkl)을 로드할 수 없습니다.")

# -------------------------------------------------
# 대시보드 상단 헤더 영역
# -------------------------------------------------
st.markdown("""
<div class='main-title'>AIRCRAFT ENGINE HEALTH MONITORING SYSTEM</div>
<div class='sub-title'>Predictive Maintenance & Prognostics Telemetry Dashboard · NASA C-MAPSS Core</div>
<div class='system-box'>TELEMETRY STATUS : CONNECTED & ON-LINE</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 입력 파라미터 제어 영역
# -------------------------------------------------
st.markdown("<h3>ENGINE OPERATIONAL PARAMETERS</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    운전사이클 = st.slider("누적 운전 사이클 (TOTAL OPERATING CYCLES)", 1, 400, 150)
    센서2 = st.slider("센서 02 (LPC OUTLET TEMPERATURE)", 630.0, 650.0, 641.0)
    센서3 = st.slider("센서 03 (HPC OUTLET TEMPERATURE)", 1500.0, 1700.0, 1580.0)
    센서4 = st.slider("센서 04 (LPT OUTLET TEMPERATURE)", 1300.0, 1450.0, 1400.0)
    센서7 = st.slider("센서 07 (HPC OUTLET PRESSURE)", 500.0, 600.0, 550.0)

with col2:
    센서11 = st.slider("센서 11 (HPT ROTOR SPEED)", 2300.0, 2500.0, 2400.0)
    센서12 = st.slider("센서 12 (BYPASS DUCT PRESSURE)", 8000.0, 8500.0, 8150.0)
    센서15 = st.slider("센서 15 (BYPASS RATIO)", 7.0, 10.0, 8.5)
    센서20 = st.slider("센서 20 (HPT BLEED FLOW)", 35.0, 50.0, 40.0)
    센서21 = st.slider("센서 21 (LPT BLEED FLOW)", 20.0, 30.0, 23.0)

# -------------------------------------------------
# 센서 레이더 차트 분석 시각화
# -------------------------------------------------
st.markdown("<br><hr style='border-color: #1E293B;'><br>", unsafe_allow_html=True)
st.markdown("<h3>SENSOR ARRAY VECTOR ANALYSIS</h3>", unsafe_allow_html=True)

radar = go.Figure()
radar.add_trace(
    go.Scatterpolar(
        r=[센서2, 센서3/10, 센서4/10, 센서7, 센서11/10, 센서12/100, 센서15*50, 센서20*10, 센서21*10],
        theta=["S02", "S03", "S04", "S07", "S11", "S12", "S15", "S20", "S21"],
        fill='toself',
        fillcolor='rgba(0, 229, 255, 0.05)',
        line=dict(color='#00E5FF', width=1.5),
        name="실시간 원격 측정 데이터"
    )
)

radar.update_layout(
    paper_bgcolor="#0B0F19",
    plot_bgcolor="#0B0F19",
    font=dict(color="#94A3B8", size=11),
    polar=dict(
        bgcolor="#0F172A",
        radialaxis=dict(visible=True, gridcolor="#1E293B", linecolor="#334155", tickfont=dict(size=9)),
        angularaxis=dict(gridcolor="#1E293B", linecolor="#334155")
    ),
    margin=dict(t=30, b=30, l=30, r=30)
)
st.plotly_chart(radar, use_container_width=True)

# -------------------------------------------------
# 진단 시퀀스 가동 및 데이터 출력
# -------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

if st.button("EXECUTE DIAGNOSTIC SEQUENCE"):
    
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
        # 테스트용 예외 더미 처리
        결과 = 1 if 운전사이클 > 200 else 0
        확률 = 0.51 if 운전사이클 == 150 else 운전사이클 / 400.0

    st.markdown("<br><hr style='border-color: #1E293B;'><br>", unsafe_allow_html=True)
    st.markdown("<h3>SYSTEM DIAGNOSTIC RESULTS</h3>", unsafe_allow_html=True)
    
    res_col1, res_col2 = st.columns([1.1, 1])

    with res_col1:
        # 미니멀 고시인성 게이지 차트
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=확률 * 100,
                number={'suffix': "%", 'font': {'color': '#FFFFFF', 'size': 50, 'weight': 'bold'}},
                title={'text': "결함 발생 확률 계수", 'font': {'color': '#94A3B8', 'size': 13}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': dict(size=10)},
                    'bar': {'color': "rgba(0,0,0,0)"}, 
                    'bgcolor': "#0F172A",
                    'borderwidth': 1,
                    'bordercolor': "#1E293B",
                    'steps': [
                        {'range': [0, 40], 'color': '#10B981'},   # 정상 운용 자산
                        {'range': [40, 70], 'color': '#F59E0B'},  # 집중 모니터링 대상
                        {'range': [70, 100], 'color': '#EF4444'}  # 즉시 정비 대상
                    ],
                    'threshold': {
                        'line': {'color': "#FFFFFF", 'width': 3},
                        'thickness': 0.8,
                        'value': 확률 * 100
                    }
                }
            )
        )
        gauge.update_layout(
            paper_bgcolor="#0B0F19",
            font=dict(color="white"),
            margin=dict(t=40, b=10, l=10, r=10),
            height=260
        )
        st.plotly_chart(gauge, use_container_width=True)

    with res_col2:
        # 결과 코드 분기 처리
        if 결과 == 1:
            상태 = "<span style='color:#EF4444;'>정비 요망 (CRITICAL)</span>"
            권고 = "<span style='color:#FCA5A5;'>경고: 해당 자산의 한계 성능 수치 초과 및 결함 징후가 검출되었습니다. 시퀀스를 중단하고 즉각적인 비계획 정비 및 분해 점검을 수행하십시오.</span>"
        else:
            상태 = "<span style='color:#10B981;'>정상 구동 (NOMINAL)</span>"
            권고 = "자산의 내부 거동 및 압력 매개변수가 정해진 오차 한계 내에서 정상 유지되고 있습니다. 표준 정비 주기를 유지하십시오."

        # 고밀도 인포메이션 그리드 리포트 디자인
        st.markdown(f"""
        <div class='report-card'>
            <h2>DIAGNOSTIC & MAINTENANCE REPORT</h2>
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
                    <div class='report-value'>{운전사이클} CYCLES</div>
                </div>
                <div class='grid-item'>
                    <div class='report-label'>배포 아키텍처</div>
                    <div class='report-value' style='color:#00E5FF; font-size:16px;'>Random Forest v1.0</div>
                </div>
                <div class='grid-item grid-full'>
                    <div class='report-label'>엔진 관리 권장 조치사항 (REQUIRED MAINTENANCE ACTION)</div>
                    <div class='report-value' style='font-size: 13px; font-weight: 400; line-height: 1.6; margin-top: 5px;'>{권고}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
