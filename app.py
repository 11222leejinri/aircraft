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
# 프리미엄 우주항공 MCC 스타일 인라인 CSS
# -------------------------------------------------
st.markdown("""
<style>
/* 전체 심우주 다크 테마 배경 */
.stApp {
    background-color: #080B11; 
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
}

.block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

/* 메인 타이틀 */
.main-title {
    text-align: center;
    color: #FFFFFF;
    font-size: 38px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 8px;
}

/* 서브 타이틀 */
.sub-title {
    text-align: center;
    color: #64748B;
    font-size: 15px;
    font-weight: 500;
    letter-spacing: 1px;
    margin-bottom: 35px;
}

/* 실시간 시스템 상단 바 */
.system-box {
    background: linear-gradient(90deg, rgba(0, 210, 255, 0.03) 0%, rgba(0, 210, 255, 0.15) 50%, rgba(0, 210, 255, 0.03) 100%);
    border-top: 1px solid rgba(0, 210, 255, 0.3);
    border-bottom: 1px solid rgba(0, 210, 255, 0.3);
    padding: 10px;
    margin-bottom: 45px;
    color: #00D2FF;
    text-align: center;
    font-weight: 700;
    letter-spacing: 2px;
    font-size: 13px;
}

/* 세련된 진단 결과 카드 레이아웃 */
.report-card {
    background: #111622;
    border: 1px solid #1E2638;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
    margin-top: 10px;
}

.report-card h2 {
    color: #FFFFFF;
    font-size: 22px;
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 20px;
    border-bottom: 1px solid #2A354F;
    padding-bottom: 12px;
}

/* 내부 그리드 아이템 정렬 */
.grid-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.grid-item {
    background: #182030;
    padding: 15px 20px;
    border-radius: 8px;
    border: 1px solid #243147;
}

.report-label {
    color: #94A3B8;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.report-value {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 700;
}

/* 권장 조치사항은 가로로 길게 배치 */
.grid-full {
    grid-column: span 2;
    background: #1E1B29;
    border: 1px solid #3B2A4A;
}

/* 미래지향적 제어 버튼 */
.stButton button {
    width: 100%;
    height: 55px;
    background: linear-gradient(135deg, #0052D4 0%, #4364F7 50%, #6FB1FC 100%);
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1px;
    border: none;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(67, 100, 247, 0.4);
    transition: all 0.3s ease;
    margin-top: 20px;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(67, 100, 247, 0.6);
    background: linear-gradient(135deg, #0052D4 0%, #4D73FF 50%, #82BFFF 100%);
}

/* 슬라이더 스타일 커스텀 */
.stSlider label {
    color: #CBD5E1 !important;
    font-weight: 500;
    font-size: 13px;
}

h2, h3 {
    color: #FFFFFF;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# AI 모델 불러오기
# -------------------------------------------------
try:
    모델 = joblib.load("aircraft_model.pkl")
    스케일러 = joblib.load("aircraft_scaler.pkl")
    model_loaded = True
except:
    model_loaded = False
    st.error("⚠️ 모델 파일을 찾을 수 없습니다. (aircraft_model.pkl, aircraft_scaler.pkl)")

# -------------------------------------------------
# 대시보드 헤더
# -------------------------------------------------
st.markdown("""
<div class='main-title'>항공기 엔지니어링 텔레메트리 시스템</div>
<div class='sub-title'>인공지능 기반 예측 정비 대시보드 · NASA C-MAPSS 데이터셋</div>
<div class='system-box'>원격 제어 상태 : 실시간 모니터링 및 시퀀스 대기 중</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 입력 영역 (엔진 파라미터 제어)
# -------------------------------------------------
st.markdown("<h3>⚙️ 엔진 운전 매개변수 설정</h3>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    운전사이클 = st.slider("누적 운전 사이클 (Operating Cycle)", 1, 400, 150)
    센서2 = st.slider("센서 2 (저압 압축기 출구 온도)", 630.0, 650.0, 641.0)
    센서3 = st.slider("센서 3 (고압 압축기 출구 온도)", 1500.0, 1700.0, 1580.0)
    센서4 = st.slider("센서 4 (저압 터빈 출구 온도)", 1300.0, 1450.0, 1400.0)
    센서7 = st.slider("센서 7 (고압 압축기 출구 압력)", 500.0, 600.0, 550.0)

with col2:
    센서11 = st.slider("센서 11 (고압 터빈 속도)", 2300.0, 2500.0, 2400.0)
    센서12 = st.slider("센서 12 (바이패스 덕트 압력)", 8000.0, 8500.0, 8150.0)
    센서15 = st.slider("센서 15 (바이패스 비율)", 7.0, 10.0, 8.5)
    센서20 = st.slider("센서 20 (고압 터빈 블리드 유량)", 35.0, 50.0, 40.0)
    센서21 = st.slider("센서 21 (저압 터빈 블리드 유량)", 20.0, 30.0, 23.0)

# -------------------------------------------------
# 센서 레이더 차트
# -------------------------------------------------
st.markdown("<br><hr style='border-color: #1E2638;'><br>", unsafe_allow_html=True)
st.markdown("<h3>🛰️ 센서 어레이 프로필 분석</h3>", unsafe_allow_html=True)

radar = go.Figure()
radar.add_trace(
    go.Scatterpolar(
        r=[센서2, 센서3/10, 센서4/10, 센서7, 센서11/10, 센서12/100, 센서15*50, 센서20*10, 센서21*10],
        theta=["센서2", "센서3", "센서4", "센서7", "센서11", "센서12", "센서15", "센서20", "센서21"],
        fill='toself',
        fillcolor='rgba(0, 210, 255, 0.1)',
        line=dict(color='#00D2FF', width=2),
        name="실시간 원격 데이터"
    )
)

radar.update_layout(
    paper_bgcolor="#080B11",
    plot_bgcolor="#080B11",
    font=dict(color="#94A3B8", size=12),
    polar=dict(
        bgcolor="#111622",
        radialaxis=dict(visible=True, gridcolor="#1E2638", linecolor="#243147"),
        angularaxis=dict(gridcolor="#1E2638", linecolor="#243147")
    ),
    margin=dict(t=30, b=30, l=30, r=30)
)
st.plotly_chart(radar, use_container_width=True)

# -------------------------------------------------
# 진단 시퀀스 가동 및 결과 출력
# -------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

if st.button("AI 진단 시퀀스 시작 (RUN DIAGNOSTICS)"):
    
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
        # 모델 부재 시 예시 더미 데이터 처리
        결과 = 1 if 운전사이클 > 200 else 0
        확률 = 0.51 if 운전사이클 == 150 else 운전사이클 / 400.0

    st.markdown("<br><hr style='border-color: #1E2638;'><br>", unsafe_allow_html=True)
    st.markdown("<h3>📊 시스템 진단 결과 리포트</h3>", unsafe_allow_html=True)
    
    res_col1, res_col2 = st.columns([1.1, 1])

    with res_col1:
        # 게이지 차트 스타일 고도화
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=확률 * 100,
                number={'suffix': "%", 'font': {'color': '#FFFFFF', 'size': 55, 'weight': 'bold'}},
                title={'text': "엔진 고장 발생 위험도", 'font': {'color': '#94A3B8', 'size': 15}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
                    'bar': {'color': "rgba(0,0,0,0)"}, 
                    'bgcolor': "#111622",
                    'borderwidth': 1,
                    'bordercolor': "#1E2638",
                    'steps': [
                        {'range': [0, 40], 'color': '#10B981'},   # 안정 (초록)
                        {'range': [40, 70], 'color': '#F59E0B'},  # 유의 (노랑)
                        {'range': [70, 100], 'color': '#EF4444'}  # 위험 (빨강)
                    ],
                    'threshold': {
                        'line': {'color': "#FFFFFF", 'width': 4},
                        'thickness': 0.8,
                        'value': 확률 * 100
                    }
                }
            )
        )
        gauge.update_layout(
            paper_bgcolor="#080B11",
            font=dict(color="white"),
            margin=dict(t=40, b=10, l=10, r=10),
            height=280
        )
        st.plotly_chart(gauge, use_container_width=True)

    with res_col2:
        # 상태에 따른 한글 텍스트 및 동적 컬러 정의
        if 결과 == 1:
            상태 = "<span style='color:#EF4444;'>정비 필요 (CRITICAL)</span>"
            권고 = "<span style='color:#FCA5A5;'>⚠️ 경고: 엔진 결함 확산 가능성이 높습니다. 즉각적인 정비 및 정밀 점검 조치를 수행하십시오.</span>"
        else:
            상태 = "<span style='color:#10B981;'>정상 구동 (NOMINAL)</span>"
            권고 = "엔진이 허용 표준 오차 범위 내에서 안정적으로 작동하고 있습니다. 주기적인 정비 일정을 유지하십시오."

        # 한글 컴포넌트화 된 프리미엄 리포트 카드 디자인
        st.markdown(f"""
        <div class='report-card'>
            <h2>엔진 상태 미션 로그 (MISSION LOG)</h2>
            <div class='grid-container'>
                <div class='grid-item'>
                    <div class='report-label'>엔진 시스템 상태</div>
                    <div class='report-value'>{상태}</div>
                </div>
                <div class='grid-item'>
                    <div class='report-label'>연산된 위험 계수</div>
                    <div class='report-value'>{확률*100:.2f} %</div>
                </div>
                <div class='grid-item'>
                    <div class='report-label'>현재 기록된 운전 사이클</div>
                    <div class='report-value'>{운전사이클} Cycles</div>
                </div>
                <div class='grid-item'>
                    <div class='report-label'>분석 알고리즘</div>
                    <div class='report-value' style='color:#00D2FF; font-size:15px;'>Random Forest v1.0</div>
                </div>
                <div class='grid-item grid-full'>
                    <div class='report-label'>권장 조치 사항 (ACTION REQUIRED)</div>
                    <div class='report-value' style='font-size: 15px; font-weight: 500; line-height: 1.5; margin-top: 5px;'>{권고}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
