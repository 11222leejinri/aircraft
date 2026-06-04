import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px

# -------------------------------------------------
# 페이지 설정
# -------------------------------------------------

st.set_page_config(
    page_title="항공기 엔진 예방정비 AI",
    page_icon="✈️",
    layout="wide"
)

# -------------------------------------------------
# CSS
# -------------------------------------------------

st.markdown("""
<style>

.stApp{
background: linear-gradient(
135deg,
#08111f,
#0f2037,
#142d4c
);
color:white;
}

.main-title{
font-size:48px;
font-weight:800;
text-align:center;
color:white;
}

.sub-title{
text-align:center;
font-size:20px;
color:#d9e6f2;
}

.card{
background:rgba(255,255,255,0.08);
padding:20px;
border-radius:20px;
backdrop-filter: blur(10px);
border:1px solid rgba(255,255,255,0.1);
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

st.markdown(
    "<div class='main-title'>✈️ 항공기 엔진 예방정비 AI 시스템</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='sub-title'>NASA C-MAPSS 데이터를 활용한 항공기 엔진 상태 분석</div>",
    unsafe_allow_html=True
)

st.write("")

# -------------------------------------------------
# 입력
# -------------------------------------------------

st.markdown("### 🔧 엔진 센서 입력")

col1, col2 = st.columns(2)

with col1:

    운전사이클 = st.slider(
        "운전 사이클",
        1,
        400,
        150
    )

    센서2 = st.slider(
        "센서2",
        630.0,
        650.0,
        641.0
    )

    센서3 = st.slider(
        "센서3",
        1500.0,
        1700.0,
        1580.0
    )

    센서4 = st.slider(
        "센서4",
        1300.0,
        1450.0,
        1400.0
    )

    센서7 = st.slider(
        "센서7",
        500.0,
        600.0,
        550.0
    )

with col2:

    센서11 = st.slider(
        "센서11",
        2300.0,
        2500.0,
        2400.0
    )

    센서12 = st.slider(
        "센서12",
        8000.0,
        8500.0,
        8150.0
    )

    센서15 = st.slider(
        "센서15",
        7.0,
        10.0,
        8.5
    )

    센서20 = st.slider(
        "센서20",
        35.0,
        50.0,
        40.0
    )

    센서21 = st.slider(
        "센서21",
        20.0,
        30.0,
        23.0
    )

# -------------------------------------------------
# 센서 시각화
# -------------------------------------------------

센서데이터 = pd.DataFrame({
    "센서":[
        "센서2",
        "센서3",
        "센서4",
        "센서7",
        "센서11",
        "센서12",
        "센서15",
        "센서20",
        "센서21"
    ],
    "값":[
        센서2,
        센서3,
        센서4,
        센서7,
        센서11,
        센서12,
        센서15,
        센서20,
        센서21
    ]
})

fig = px.bar(
    센서데이터,
    x="센서",
    y="값",
    title="📊 입력된 센서 상태"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -------------------------------------------------
# 예측
# -------------------------------------------------

if st.button("🚀 AI 분석 시작"):

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

    입력값 = 스케일러.transform(
        입력값
    )

    결과 = 모델.predict(
        입력값
    )[0]

    확률 = 모델.predict_proba(
        입력값
    )[0][1]

    st.write("")
    st.markdown("---")

    # --------------------------
    # 게이지
    # --------------------------

    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=확률*100,
            title={
                'text':'정비 위험도'
            },
            gauge={
                'axis':{
                    'range':[0,100]
                },
                'bar':{
                    'thickness':0.35
                },
                'steps':[
                    {'range':[0,40]},
                    {'range':[40,70]},
                    {'range':[70,100]}
                ]
            }
        )
    )

    st.plotly_chart(
        gauge,
        use_container_width=True
    )

    # --------------------------
    # 결과 카드
    # --------------------------

    if 결과 == 1:

        st.error(
            f"""
⚠️ 정비 필요

예상 위험도 : {확률*100:.1f}%

엔진 성능 저하가 감지되었습니다.
정비 점검을 권장합니다.
"""
        )

    else:

        st.success(
            f"""
✅ 정상 상태

예상 위험도 : {확률*100:.1f}%

현재 엔진 상태는 안정적입니다.
"""
        )

    # --------------------------
    # 리포트
    # --------------------------

    st.markdown("### 📋 AI 분석 리포트")

    st.info(
        f"""
운전 사이클: {운전사이클}

분석 모델: Random Forest

예측 결과: {'정비 필요' if 결과==1 else '정상'}

위험도: {확률*100:.1f}%
"""
    )