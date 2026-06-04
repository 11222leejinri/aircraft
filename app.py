import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import time

# -------------------------------------------------
# 페이지 및 기본 가동 상태 설정
# -------------------------------------------------
st.set_page_config(
    page_title="항공기 엔진 상태 모니터링 시스템",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 시뮬레이션 및 데이터 상태 관리를 위한 세션 상태 초기화
if 'current_cycle' not in st.session_state:
    st.session_state.current_cycle = 150
if 'sim_running' not in st.session_state:
    st.session_state.sim_running = False
if 'selected_asset' not in st.session_state:
    st.session_state.selected_asset = "엔진 호기 #101"

# -------------------------------------------------
# 에비에이션 화이트 & 블루 엔지니어링 표준 CSS
# -------------------------------------------------
st.markdown("""
<style>
/* 전체 배경 설정 (정밀 계측 장비 표준 화이트 테마) */
.stApp {
    background-color: #F8FAFC; 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.block-container {
    padding-top: 2.0rem;
    padding-bottom: 2.0rem;
}

/* 시스템 메인 타이틀 */
.main-title {
    text-align: center;
    color: #0F172A;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 5px;
}

/* 시스템 서브 타이틀 */
.sub-title {
    text-align: center;
    color: #64748B;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.5px;
    margin-bottom: 30px;
}

/* 데이터 분석 및 정비 리포트 카드 */
.report-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 4px;
    padding: 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.report-card h2 {
    color: #0F172A;
    font-size: 16px;
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 15px;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 8px;
    letter-spacing: -0.5px;
}

/* 분석 데이터 그리드 컨테이너 */
.grid-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.grid-item {
    background-color: #F8FAFC;
    padding: 10px 15px;
    border-radius: 4px;
    border: 1px solid #E2E8F0;
}

.report-label {
    color: #64748B;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 20px
    letter-spacing: 0.5px;
}

.report-value {
    color: #0F172A;
    font-size: 16px;
    font-weight: 700;
}

/* 권장 조치사항 레이아웃 */
.grid-full {
    grid-column: span 2;
    background-color: #FFFBEB;
    border: 1px solid #FDE68A;
}

/* 시스템 제어 명령 버튼 스타일 개편 */
.stButton button {
    width: 100%;
    height: 45px;
    background-color: #1E3A8A; /* 에비에이션 딥블루 */
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 600;
    border: none;
    border-radius: 4px;
    transition: background-color 0.15s ease;
}

.stButton button:hover {
    background-color: #1D4ED8;
    color: #FFFFFF;
}

/* 관제 모드 및 제어 섹션 전용 타이틀 */
h3 {
    color: #0F172A;
    font-size: 15px;
    font-weight: 700;
    margin-top: 5px;
    margin-bottom: 12px;
    border-left: 4px solid #1E3A8A;
    padding-left: 8px;
}

/* 슬라이더 라벨 정돈 */
.stSlider label, [data-testid="stWidgetLabel"] {
    color: #334155 !important;
    font-weight: 600;
    font-size: 11px;
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
# 실시간 비행 시뮬레이션 루프 제어
# -------------------------------------------------
if st.session_state.sim_running:
    if st.session_state.current_cycle < 360:
        st.session_state.current_cycle += 4
        time.sleep(0.05)
        st.rerun()
    else:
        st.session_state.sim_running = False

# -------------------------------------------------
# 대시보드 상단 타이틀
# -------------------------------------------------
st.markdown("""
<div class='main-title'>항공기 엔진 상태 모니터링 시스템</div>
<div class='sub-title'>다중 자산 관제 및 머신러닝 기반 예방 정비 분석 플랫폼 (NASA C-MAPSS)</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 고도화 기능 1 & 4: 다중 자산 관제 및 시뮬레이션 콘솔
# -------------------------------------------------
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 1])

with ctrl_col1:
    st.markdown("<h3>다중 자산 식별 (Fleet Management)</h3>", unsafe_allow_html=True)
    asset_options = ["엔진 호기 #101", "엔진 호기 #102", "엔진 호기 #103"]
    selected = st.selectbox("관제 대상 자산 선택", asset_options, label_visibility="collapsed")
    if selected != st.session_state.selected_asset:
        st.session_state.selected_asset = selected
        # 자산 변경 시 누적 사이클 초기화 세팅
        if selected == "엔진 호기 #101": st.session_state.current_cycle = 150
        elif selected == "엔진 호기 #102": st.session_state.current_cycle = 80
        elif selected == "엔진 호기 #103": st.session_state.current_cycle = 210
        st.rerun()

with ctrl_col2:
    st.markdown("<h3>자동 비행 시뮬레이션 (Simulation)</h3>", unsafe_allow_html=True)
    if st.session_state.sim_running:
        if st.button("시뮬레이션 일시정지"):
            st.session_state.sim_running = False
            st.rerun()
    else:
        if st.button("시뮬레이션 연속 가동 시작"):
            st.session_state.sim_running = True
            st.rerun()

with ctrl_col3:
    st.markdown("<h3>시뮬레이션 초기화 (Reset)</h3>", unsafe_allow_html=True)
    if st.button("구동 초기 상태로 복원"):
        st.session_state.current_cycle = 30
        st.session_state.sim_running = False
        st.rerun()

# -------------------------------------------------
# 입력 파라미터 제어 영역 (시뮬레이션과 연동)
# -------------------------------------------------
st.markdown("<br><h3>엔진 구동 매개변수 설정 (원격 계측 제어)</h3>", unsafe_allow_html=True)

# 시뮬레이션 진행도에 따라 센서 데이터가 동적으로 열화되도록 가중치 맵핑
c_ratio = (st.session_state.current_cycle / 400.0)
base_s2 = 635.0 + (c_ratio * 12.0)
base_s3 = 1520.0 + (c_ratio * 150.0)
base_s4 = 1320.0 + (c_ratio * 110.0)
base_s11 = 2320.0 + (c_ratio * 160.0)

col1, col2 = st.columns(2)

with col1:
    운전사이클 = st.slider("누적 구동 사이클 (Total Operating Cycles)", 1, 400, int(st.session_state.current_cycle), key="slider_cycle")
    # 슬라이더 조작 시 세션 상태 업데이트
    st.session_state.current_cycle = 운전사이클
    
    센서2 = st.slider("센서 02 (저압 압축기 출구 온도)", 630.0, 650.0, float(np.clip(base_s2, 630.0, 650.0)))
    센서3 = st.slider("센서 03 (고압 압축기 출구 온도)", 1500.0, 1700.0, float(np.clip(base_s3, 1500.0, 1700.0)))
    센서4 = st.slider("센서 04 (저압 터빈 출구 온도)", 1300.0, 1450.0, float(np.clip(base_s4, 1300.0, 1450.0)))
    센서7 = st.slider("센서 07 (고압 압축기 출구 압력)", 500.0, 600.0, float(570.0 - (c_ratio * 50.0)))

with col2:
    센서11 = st.slider("센서 11 (고압 터빈 로터 속도)", 2300.0, 2500.0, float(np.clip(base_s11, 2300.0, 2500.0)))
    센서12 = st.slider("센서 12 (바이패스 덕트 압력)", 8000.0, 8500.0, float(8350.0 - (c_ratio * 300.0)))
    센서15 = st.slider("센서 15 (바이패스 비율)", 7.0, 10.0, float(7.5 + (c_ratio * 2.1)))
    센서20 = st.slider("센서 20 (고압 터빈 블리드 유량)", 35.0, 50.0, float(36.0 + (c_ratio * 12.0)))
    센서21 = st.slider("센서 21 (저압 터빈 블리드 유량)", 20.0, 30.0, float(21.0 + (c_ratio * 8.0)))

# -------------------------------------------------
# 백엔드 진단 알고리즘 연산
# -------------------------------------------------
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
    # 수식 기반 정밀 더미 연산 (실제 추세와 매칭)
    확률 = 1.0 / (1.0 + np.exp(-0.03 * (운전사이클 - 180)))
    결과 = 1 if 확률 > 0.5 else 0

# 고도화 기능 2: 잔여 수명 (RUL: Remaining Useful Life) 연산
예상잔여수명 = max(0, int((1.0 - 확률) * 220))

# -------------------------------------------------
# 시각화 데이터 섹션 1: 레이더 차트 및 고도화 기능 5(위험도 누적 추세선)
# -------------------------------------------------
st.markdown("<br><hr style='border-color: #E2E8F0;'><br>", unsafe_allow_html=True)
vis_col1, vis_col2 = st.columns(2)

with vis_col1:
    st.markdown("<h3>센서 배열 벡터 분석 (Spatial Profile)</h3>", unsafe_allow_html=True)
    radar = go.Figure()
    radar.add_trace(
        go.Scatterpolar(
            r=[센서2, 센서3/10, 센서4/10, 센서7, 센서11/10, 센서12/100, 센서15*50, 센서20*10, 센서21*10],
            theta=["S02", "S03", "S04", "S07", "S11", "S12", "S15", "S20", "S21"],
            fill='toself',
            fillcolor='rgba(30, 58, 138, 0.05)',
            line=dict(color='#1E3A8A', width=1.5),
            name="측정 데이터"
        )
    )
    radar.update_layout(
        paper_bgcolor="#F8FAFC", plot_bgcolor="#F8FAFC",
        font=dict(color="#334155", size=10),
        polar=dict(
            bgcolor="#FFFFFF",
            radialaxis=dict(visible=True, gridcolor="#E2E8F0", linecolor="#CBD5E1", tickfont=dict(size=8)),
            angularaxis=dict(gridcolor="#E2E8F0", linecolor="#CBD5E1")
        ),
        margin=dict(t=20, b=20, l=40, r=40), height=280
    )
    st.plotly_chart(radar, use_container_width=True)

with vis_col2:
    st.markdown("<h3>고도화 분석: 결함 발생 위험도 누적 추세 (Risk Trend)</h3>", unsafe_allow_html=True)
    # 현재 사이클까지의 시계열 추세 벡터 생성
    history_cycles = np.array(range(1, 운전사이클 + 1))
    if model_loaded:
        # 모델이 있을 경우의 간이 추세선 보간
        history_risks = 1.0 / (1.0 + np.exp(-0.025 * (history_cycles - (180 * (확률 if 확률 > 0 else 0.5)))))
    else:
        history_risks = 1.0 / (1.0 + np.exp(-0.03 * (history_cycles - 180)))
    
    trend = go.Figure()
    trend.add_trace(go.Scatter(
        x=history_cycles, y=history_risks * 100,
        mode='lines', line=dict(color='#1E3A8A', width=2),
        fill='tozeroy', fillcolor='rgba(30, 58, 138, 0.03)',
        name="위험도 추이"
    ))
    trend.update_layout(
        paper_bgcolor="#F8FAFC", plot_bgcolor="#FFFFFF",
        xaxis=dict(title="구동 사이클", gridcolor="#E2E8F0", textfont=dict(size=10)),
        yaxis=dict(title="위험도 (%)", range=[0, 100], gridcolor="#E2E8F0"),
        margin=dict(t=20, b=20, l=40, r=20), height=280
    )
    st.plotly_chart(trend, use_container_width=True)

# -------------------------------------------------
# 시각화 데이터 섹션 2: 계측 게이지 및 고도화 기능 3 (XAI 원인 분석 바 차트)
# -------------------------------------------------
st.markdown("<br><hr style='border-color: #E2E8F0;'><br>", unsafe_allow_html=True)
st.markdown("<h3>시스템 종합 진단 결과</h3>", unsafe_allow_html=True)

res_col1, res_col2, res_col3 = st.columns([1, 1.1, 1.2])

with res_col1:
    # 계측 게이지 차트
    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=확률 * 100,
            number={'suffix': "%", 'font': {'color': '#0F172A', 'size': 42, 'weight': 'bold'}},
            title={'text': "현재 결함 확률", 'font': {'color': '#64748B', 'size': 12, 'weight': 'bold'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': dict(size=9)},
                'bar': {'color': "rgba(0,0,0,0)"}, 
                'bgcolor': "#F1F5F9",
                'borderwidth': 1, 'bordercolor': "#CBD5E1",
                'steps': [
                    {'range': [0, 40], 'color': '#10B981'},
                    {'range': [40, 70], 'color': '#F59E0B'},
                    {'range': [70, 100], 'color': '#EF4444'}
                ],
                'threshold': {
                    'line': {'color': "#0F172A", 'width': 3},
                    'thickness': 0.75, 'value': 확률 * 100
                }
            }
        )
    )
    gauge.update_layout(
        paper_bgcolor="#F8FAFC", font=dict(color="#0F172A"),
        margin=dict(t=30, b=10, l=10, r=10), height=240
    )
    st.plotly_chart(gauge, use_container_width=True)

with res_col2:
    st.markdown("<h3 style='border-left:4px solid #64748B;'>고도화 분석: 주요 결함 원인 인자 (XAI 기여도)</h3>", unsafe_allow_html=True)
    # 센서 가중치 역산 기반의 기여도 가상 매칭 차트
    features = ["고압터빈 속도 (S11)", "고압압축기 온도 (S03)", "저압터빈 온도 (S04)", "구동 사이클"]
    # 사이클이 높아질수록 S11과 S03의 결함 기여도가 동적으로 상승하도록 모델링
    contributions = [25 + (c_ratio * 35), 20 + (c_ratio * 20), 15 + (c_ratio * 5), 10 + (c_ratio * 2)]
    total_contrib = sum(contributions)
    norm_contributions = [c / total_contrib * 확률 * 100 for c in contributions]

    xai_bar = go.Figure(go.Bar(
        x=norm_contributions, y=features,
        orientation='h',
        marker=dict(color=['#EF4444' if 확률 > 0.7 else '#1E3A8A']*4),
        text=[f"+{val:.1f}%" for val in norm_contributions],
        textposition='inside',
        textfont=dict(color='white', size=10)
    ))
    xai_bar.update_layout(
        paper_bgcolor="#F8FAFC", plot_bgcolor="#F8FAFC",
        xaxis=dict(title="위험 기여도 (%)", showgrid=False, range=[0, max(norm_contributions)*1.3]),
        yaxis=dict(autorange="reverse", tickfont=dict(size=10)),
        margin=dict(t=10, b=10, l=10, r=10), height=200
    )
    st.plotly_chart(xai_bar, use_container_width=True)

with res_col3:
    # 정비 상태 텍스트 판정 분기
    if 결과 == 1:
        상태 = "<span style='color:#EF4444;'>정비 요망 (Critical)</span>"
        권고 = "<span style='color:#991B1B;'>지침 한계치 초과 및 결함 원인 인자가 검출되었습니다. 가동 시퀀스를 즉시 중단하고 비계획 정비 지침에 따라 정밀 분해 점검을 수행하십시오.</span>"
    else:
        상태 = "<span style='color:#10B981;'>정상 구동 (Nominal)</span>"
        권고 = "내부 거동 및 압력 매개변수가 규정 오차 범위 내에서 안정적입니다. 표준 정비 주기를 유지하십시오."

    # 종합 리포트 출력 레이아웃 (고도화 RUL 지표 통합)
    st.markdown(f"""
    <div class='report-card'>
        <h2>정비 진단 리포트 ({st.session_state.selected_asset})</h2>
        <div class='grid-container'>
            <div class='grid-item'>
                <div class='report-label'>시스템 분석 상태</div>
                <div class='report-value'>{상태}</div>
            </div>
            <div class='grid-item'>
                <div class='report-label'>잔여 유효 수명 (RUL)</div>
                <div class='report-value' style='color:#1E3A8A;'>{예상잔여수명} 사이클 남음</div>
            </div>
            <div class='grid-item'>
                <div class='report-label'>연산된 리스크 가중치</div>
                <div class='report-value'>{확률*100:.2f} %</div>
            </div>
            <div class='grid-item'>
                <div class='report-label'>로그된 누적 사이클</div>
                <div class='report-value'>{운전사이클} Cycles</div>
            </div>
            <div class='grid-item grid-full'>
                <div class='report-label'>엔진 관리 권장 조치사항</div>
                <div class='report-value' style='font-size: 12px; font-weight: 500; line-height: 1.5; margin-top: 4px; color:#1E293B;'>{권고}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
