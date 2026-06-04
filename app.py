import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# -------------------------------------------------
# 페이지 설정
# ----------------------------------------

st.set_page_config(
    page_title="Aircraft Engine Health Monitoring",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# CSS (SpaceX / NASA Mission Control 스타일)
# -------------------------------------------------

st.markdown("""
<style>
/* 전체 배경 및 폰트 설정 */
.stApp {
    background-color: #050505; /* Deep Space Black */
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

/* 상단 여백 조절 */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* 메인 타이틀 */
.main-title {
    text-align: center;
    color: #FFFFFF;
    font-size: 46px;
    font-weight: 800;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 5px;
}

/* 서브 타이틀 */
.sub-title {
    text-align: center;
    color: #888888;
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 40px;
}

/* 시스템 상태 박스 */
.system-box {
    background: rgba(0, 82, 136, 0.1); /* Boeing Blue 투명도 */
    border-left: 4px solid #00AEEF;
    border-right: 4px solid #00AEEF;
    padding: 12px;
    margin-bottom: 40px;
    color: #00AEEF;
    text-align: center;
    font-weight: 700;
    letter-spacing: 3px;
    font-size: 14px;
    text-transform: uppercase;
}

/* 리포트 결과 박스 */
.report-box {
    background-color: #0D0D0D;
    border: 1px solid #222222;
    border-top: 4px solid #005288;
    padding: 30px;
    color: #E0E0E0;
    font-family: 'Courier New', Courier, monospace; /* 터미널 느낌의 폰트 */
}

.report-box h2 {
    color: #FFFFFF;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    letter-spacing: 2px;
    font-size: 24px;
    margin-top: 0;
}

.report-box hr {
    border-color: #333333;
}

.report-label {
    color: #888888;
    font-size: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.report-value {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 15px;
}

/* 예측 버튼 (SpaceX 스타일) */
.stButton button {
    width: 100%;
    height: 60px;
    background-color: transparent;
    color: #FFFFFF;
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 2px;
    text-transform: uppercase;
    border: 2px solid #FFFFFF;
    border-radius: 0px; /* 각진 디자인 */
    transition: all 0.3s ease;
    margin-top: 20px;
}

.stButton button:hover {
    background-color: #FFFFFF;
    color: #000000;
    border-color: #FFFFFF;
    box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
}

/* 슬라이더 라벨 색상 */
.stSlider label {
    color: #A0A0A0 !important;
    font-family: 'Courier New', Courier, monospace;
}

/* 마크다운 헤더 색상 */
h2, h3 {
    color: #FFFFFF;
    letter-spacing: 1px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 모델 불러오기
# -------------------------------------------------
# 실제 실행을 위해서는 아래 파일들이 같은 경로에 있어야 합니다.
try:
    모델 = joblib.load("aircraft_model.pkl")
    스케일러 = joblib.load("aircraft_scaler.pkl")
    model_loaded = True
except:
    model_loaded = False
    st.error("⚠️ 모델 파일을 찾을 수 없습니다. (aircraft_model.pkl, aircraft_scaler.pkl)")

# -------------------------------------------------
# 헤더 영역
# -------------------------------------------------

st.markdown("""
<div class='main-title'>
AIRCRAFT ENGINE TELEMETRY
</div>
<div class='sub-title'>
Predictive Maintenance Dashboard · NASA C-MAPSS
</div>
<div class='system-box'>
SYSTEM STATUS : ONLINE & RECORDING
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 입력 영역
# -------------------------------------------------

st.markdown("## ⚙️ FLIGHT PARAMETERS")
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    운전사이클 = st.slider("OPERATING CYCLE", 1, 400, 150)
    센서2 = st.slider("SENSOR 2 (LPC OUTLET TEMP)", 630.0, 650.0, 641.0)
    센서3 = st.slider("SENSOR 3 (HPC OUTLET TEMP)", 1500.0, 1700.0, 1580.0)
    센서4 = st.slider("SENSOR 4 (LPT OUTLET TEMP)", 1300.0, 1450.0, 1400.0)
    센서7 = st.slider("SENSOR 7 (HPC OUTLET PRESSURE)", 500.0, 600.0, 550.0)

with col2:
    센서11 = st.slider("SENSOR 11 (HPC MOTOR TEMP)", 2300.0, 2500.0, 2400.0)
    센서12 = st.slider("SENSOR 12 (BYPASS DUCT PRESSURE)", 8000.0, 8500.0, 8150.0)
    센서15 = st.slider("SENSOR 15 (BYPASS MARGIN)", 7.0, 10.0, 8.5)
    센서20 = st.slider("SENSOR 20 (HPT BLEED BLEED)", 35.0, 50.0, 40.0)
    센서21 = st.slider("SENSOR 21 (LPT BLEED)", 20.0, 30.0, 23.0)

# -------------------------------------------------
# 레이더 차트
# -------------------------------------------------
st.markdown("<br><hr style='border-color: #222;'><br>", unsafe_allow_html=True)
st.markdown("## 🛰️ SENSOR ARRAY PROFILE")

radar = go.Figure()

radar.add_trace(
    go.Scatterpolar(
        r=[
            센서2, 센서3/10, 센서4/10, 센서7, 센서11/10,
            센서12/100, 센서15*50, 센서20*10, 센서21*10
        ],
        theta=["S2", "S3", "S4", "S7", "S11", "S12", "S15", "S20", "S21"],
        fill='toself',
        fillcolor='rgba(0, 174, 239, 0.15)', /* 약간의 투명도 있는 블루 */
        line=dict(color='#00AEEF', width=2),
        name="Telemetry Data"
    )
)

radar.update_layout(
    paper_bgcolor="#050505",
    plot_bgcolor="#050505",
    font=dict(color="#A0A0A0", family="Courier New"),
    polar=dict(
        bgcolor="#0D0D0D",
        radialaxis=dict(
            visible=True,
            gridcolor="#222222",
            linecolor="#333333"
        ),
        angularaxis=dict(
            gridcolor="#222222",
            linecolor="#333333"
        )
    ),
    margin=dict(t=40, b=40, l=40, r=40)
)

st.plotly_chart(radar, use_container_width=True)

# -------------------------------------------------
# 진단 및 예측 실행
# -------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

if st.button("INITIATE DIAGNOSTICS"):
    
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
        # 모델이 없을 경우 UI 테스트를 위한 더미 데이터
        결과 = 1 if 운전사이클 > 200 else 0
        확률 = 운전사이클 / 400.0

    st.markdown("<br><hr style='border-color: #222;'><br>", unsafe_allow_html=True)
    st.markdown("## 📊 DIAGNOSTIC RESULTS")
    
    res_col1, res_col2 = st.columns([1, 1])

    with res_col1:
        # -------------------------------------------------
        # 게이지 차트 (고대비 색상)
        # -------------------------------------------------
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=확률 * 100,
                number={'suffix': "%", 'font': {'color': '#FFFFFF', 'size': 50}},
                title={'text': "FAILURE PROBABILITY", 'font': {'color': '#888888', 'size': 16, 'family': 'Courier New'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "rgba(0,0,0,0)"}, # 바 자체는 숨김 처리
                    'bgcolor': "#0D0D0D",
                    'borderwidth': 2,
                    'bordercolor': "#333333",
                    'steps': [
                        {'range': [0, 40], 'color': '#00FF00'},   /* 안전: 형광 그린 */
                        {'range': [40, 75], 'color': '#FFD700'},  /* 경고: 골드/옐로우 */
                        {'range': [75, 100], 'color': '#FF0000'}  /* 위험: 퓨어 레드 */
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 4},
                        'thickness': 0.75,
                        'value': 확률 * 100
                    }
                }
            )
        )

        gauge.update_layout(
            paper_bgcolor="#050505",
            font=dict(color="white"),
            margin=dict(t=50, b=20, l=20, r=20)
        )

        st.plotly_chart(gauge, use_container_width=True)

    with res_col2:
        # -------------------------------------------------
        # 상태 판별 및 리포트
        # -------------------------------------------------
        if 결과 == 1:
            상태 = "<span style='color:#FF0000;'>CRITICAL</span>"
            권고 = "IMMEDIATE MAINTENANCE INSPECTION REQUIRED."
        else:
            상태 = "<span style='color:#00FF00;'>NOMINAL</span>"
            권고 = "ENGINE OPERATING WITHIN EXPECTED PARAMETERS."

        st.markdown(f"""
        <div class='report-box'>
            <h2>MISSION LOG REPORT</h2>
            <hr>
            <div class='report-label'>System Status</div>
            <div class='report-value'>{상태}</div>
            
            <div class='report-label'>Computed Risk Factor</div>
            <div class='report-value'>{확률*100:.2f} %</div>
            
            <div class='report-label'>Action Required</div>
            <div class='report-value'>{권고}</div>
            
            <div class='report-label'>Logged Cycle</div>
            <div class='report-value'>{운전사이클} CYCLES</div>
            
            <div class='report-label'>Algorithm Engaged</div>
            <div class='report-value' style='color:#00AEEF;'>Random Forest Diagnostics v1.0</div>
        </div>
        """, unsafe_allow_html=True)
