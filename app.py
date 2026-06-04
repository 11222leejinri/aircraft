import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# -------------------------------------------------
# 페이지 설정
# -------------------------------------------------

st.set_page_config(
    page_title="Aircraft Engine Health Monitoring",
    layout="wide"
)

# -------------------------------------------------
# CSS
# -------------------------------------------------

st.markdown("""
<style>

.stApp{
    background-color:#0B1220;
}

.block-container{
    padding-top:1rem;
}

.main-title{
    text-align:center;
    color:#F5F7FA;
    font-size:42px;
    font-weight:700;
    letter-spacing:2px;
}

.sub-title{
    text-align:center;
    color:#8CA0B3;
    font-size:16px;
    margin-bottom:25px;
}

.system-box{
    background:#111A2C;
    border:1px solid #24344D;
    border-radius:10px;
    padding:15px;
    margin-bottom:20px;
    color:white;
    text-align:center;
    font-weight:bold;
}

.report-box{
    background:#111A2C;
    border:1px solid #24344D;
    border-radius:10px;
    padding:25px;
    color:white;
}

.stButton button{
    width:100%;
    height:60px;
    background:#1D4ED8;
    color:white;
    font-size:18px;
    font-weight:bold;
    border:none;
    border-radius:8px;
}

.stButton button:hover{
    background:#2563EB;
}

[data-testid="stSlider"]{
    padding-bottom:10px;
}

h1,h2,h3{
    color:white;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 모델 불러오기
# -------------------------------------------------

모델 = joblib.load("aircraft_model.pkl")
스케일러 = joblib.load("aircraft_scaler.pkl")

# -------------------------------------------------
# 헤더
# -------------------------------------------------

st.markdown("""
<div class='main-title'>
AIRCRAFT ENGINE HEALTH MONITORING SYSTEM
</div>

<div class='sub-title'>
Predictive Maintenance Platform using NASA C-MAPSS Dataset
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='system-box'>
SYSTEM STATUS : ONLINE
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 입력
# -------------------------------------------------

st.markdown("## Engine Parameters")

col1, col2 = st.columns(2)

with col1:

    운전사이클 = st.slider(
        "Operating Cycle",
        1, 400, 150
    )

    센서2 = st.slider(
        "Sensor 2",
        630.0, 650.0, 641.0
    )

    센서3 = st.slider(
        "Sensor 3",
        1500.0, 1700.0, 1580.0
    )

    센서4 = st.slider(
        "Sensor 4",
        1300.0, 1450.0, 1400.0
    )

    센서7 = st.slider(
        "Sensor 7",
        500.0, 600.0, 550.0
    )

with col2:

    센서11 = st.slider(
        "Sensor 11",
        2300.0, 2500.0, 2400.0
    )

    센서12 = st.slider(
        "Sensor 12",
        8000.0, 8500.0, 8150.0
    )

    센서15 = st.slider(
        "Sensor 15",
        7.0, 10.0, 8.5
    )

    센서20 = st.slider(
        "Sensor 20",
        35.0, 50.0, 40.0
    )

    센서21 = st.slider(
        "Sensor 21",
        20.0, 30.0, 23.0
    )

# -------------------------------------------------
# 레이더 차트
# -------------------------------------------------

st.markdown("## Engine Sensor Profile")

radar = go.Figure()

radar.add_trace(
    go.Scatterpolar(
        r=[
            센서2,
            센서3/10,
            센서4/10,
            센서7,
            센서11/10,
            센서12/100,
            센서15*50,
            센서20*10,
            센서21*10
        ],
        theta=[
            "S2","S3","S4",
            "S7","S11","S12",
            "S15","S20","S21"
        ],
        fill='toself',
        name="Engine Profile"
    )
)

radar.update_layout(
    paper_bgcolor="#0B1220",
    plot_bgcolor="#0B1220",
    font=dict(color="white"),
    polar=dict(
        bgcolor="#111A2C",
        radialaxis=dict(
            visible=True
        )
    ),
    title="Engine Sensor Status"
)

st.plotly_chart(
    radar,
    use_container_width=True
)

# -------------------------------------------------
# 예측
# -------------------------------------------------

if st.button("RUN DIAGNOSTIC"):

    입력값 = pd.DataFrame(
        [[
            운전사이클,
            센서2,
            센서3,
            센서4,
            센서7,
            센서11,
            센서12,
            센서15,
            센서20,
            센서21
        ]],
        columns=[
            '운전사이클',
            '센서2',
            '센서3',
            '센서4',
            '센서7',
            '센서11',
            '센서12',
            '센서15',
            '센서20',
            '센서21'
        ]
    )

    입력값 = 스케일러.transform(입력값)

    결과 = 모델.predict(입력값)[0]

    try:
        확률 = 모델.predict_proba(입력값)[0][1]
    except:
        확률 = 0.5

    st.markdown("---")

    # -------------------------------------------------
    # 게이지
    # -------------------------------------------------

    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=확률*100,
            title={
                "text":"ENGINE FAILURE RISK (%)"
            },
            gauge={
                "axis":{"range":[0,100]},
                "bar":{"color":"#3B82F6"},
                "bgcolor":"#111A2C",
                "borderwidth":2,
                "bordercolor":"#24344D",
                "steps":[
                    {"range":[0,40],"color":"#10B981"},
                    {"range":[40,70],"color":"#F59E0B"},
                    {"range":[70,100],"color":"#EF4444"}
                ]
            }
        )
    )

    gauge.update_layout(
        paper_bgcolor="#0B1220",
        font=dict(color="white")
    )

    st.plotly_chart(
        gauge,
        use_container_width=True
    )

    # -------------------------------------------------
    # 상태
    # -------------------------------------------------

    if 결과 == 1:

        상태 = "CRITICAL"
        권고 = "Immediate maintenance inspection recommended."

    else:

        상태 = "NORMAL"
        권고 = "Engine operating within expected range."

    # -------------------------------------------------
    # 리포트
    # -------------------------------------------------

    st.markdown(f"""
    <div class='report-box'>

    <h2>AIRCRAFT HEALTH REPORT</h2>

    <hr>

    <b>Engine Condition</b><br>
    {상태}

    <br><br>

    <b>Failure Probability</b><br>
    {확률*100:.1f} %

    <br><br>

    <b>Maintenance Recommendation</b><br>
    {권고}

    <br><br>

    <b>Operating Cycle</b><br>
    {운전사이클}

    <br><br>

    <b>Model</b><br>
    Random Forest Classifier

    </div>
    """, unsafe_allow_html=True)
