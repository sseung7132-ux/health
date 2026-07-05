import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import matplotlib.font_manager as fm

# 1. 폰트 경로를 직접 검색
nanum_fonts = [f.fname for f in fm.fontManager.ttflist if 'Nanum' in f.name]

if nanum_fonts:
    # 2. 발견된 첫 번째 나눔 폰트를 매니저에 강제 등록
    fm.fontManager.addfont(nanum_fonts[0])
    font_name = fm.FontProperties(fname=nanum_fonts[0]).get_name()
    plt.rc('font', family=font_name)
else:
    # 3. 만약 시스템에 없으면 기본 경로에서 강제 탐색 시도
    import os
    alternative_path = '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'
    if os.path.exists(alternative_path):
        fm.fontManager.addfont(alternative_path)
        font_name = fm.FontProperties(fname=alternative_path).get_name()
        plt.rc('font', family=font_name)
    else:
        # 안전장치: 폰트가 정말 없을 때 우회 설정
        plt.rc('font', family='sans-serif')

# 폰트를 '나눔바른고딕'으로 설정
#plt.rc('font', family='NanumBarunGothic') 
#plt.rc('font' , family='Malgun Gothic') 

plt.rcParams['axes.unicode_minus'] = False

# 1. 수집된 데이터 예시 (가상 데이터 15명 분량)
# 표본조사표 -->  나중에  친구들이나 지인들한테 조사양식을
data = {
    "이름": [f"참여자{i}" for i in range(1, 16)],
    "수면시간": [7.5, 6.0, 5.5, 8.0, 6.5, 7.0, 5.0, 8.5, 6.0, 7.0, 7.5, 5.5, 6.5, 8.0, 6.0],
    "운동시간": [1.5, 0.5, 0.0, 1.0, 2.0, 0.5, 0.0, 1.2, 0.8, 1.5, 0.0, 0.5, 1.0, 1.5, 0.5],
    "걸음수": [12000, 6000, 3500, 9000, 14000, 7000, 3000, 10000, 8000, 11000, 4000, 5000, 8500, 13000, 6500],
    "주관적건강상태": [5, 3, 2, 4, 5, 3, 1, 4, 3, 5, 2, 2, 4, 5, 3],  # 1(매우나쁨) ~ 5(매우좋음)
    "피로도": [1, 4, 5, 2, 1, 3, 5, 1, 3, 2, 4, 4, 2, 1, 4]  # 1(안피곤) ~ 5(매우피곤)
}

df = pd.DataFrame(data)

# 2. 기초 통계 분석 및 상관관계 출력
#print("=== 주요 건강 지표 평균값 ===")
#print(df[["수면시간", "운동시간", "걸음수"]].mean())
#print("\n=== 상관계수 행렬 ===")
#print(df[["수면시간", "운동시간", "걸음수", "주관적건강상태", "피로도"]].corr())

# - 웹 페이지 부분 -#
st.set_page_config(page_title="맞춤형 헬스케어 피드백 시스템" , layout="wide")

st.title(" [맞춤형 헬스케어 피드백 시스템]")
st.markdown("---------------------")

# 입력 부분 #
st.sidebar.header("📊 사용자 건강 데이터 입력", divider="rainbow")
name =  st.sidebar.text_input("이름을 입력하세요" , "이승미");
height = st.sidebar.number_input("키(cm)" , min_value=100.0 , max_value=250.0, value=168.0) / 100
weight = st.sidebar.number_input("몸무게(kg)", min_value=30.0, max_value=200.0, value=48.0)


st.sidebar.markdown("---------------------")
st.sidebar.header(" # 일일생활 습관입력(수면,운동시간, 걸음수)")
sleep_time = st.sidebar.slider("일일 평균  수면 시간(시간)"  ,0.0 , 24.0, 5.5, step=0.5)
exercise_time = st.sidebar.slider("일일 평균 운동 시간(시간)" ,0.0 , 54.0, 5.5, step=0.1)
steps= st.sidebar.slider("일일 평균 걸음수 "  , min_value=0 , max_value=50000, value=8500 ,step=5000)

# 분석 버튼 #
if st.sidebar.button(" 건강 상태 분석 " , type="primary"):
    #1. bmi 지표 계산
    bmi = weight / (height ** 2)
    if bmi < 18.5:  bmi_status ="저체중" 
    elif bmi < 23 : bmi_status ="정상체중" 
    elif bmi < 25 : bmi_status ="과체중" 
    else  : bmi_status ="비만" 
    #1. 점수 계산
    score = 0
    score += 30 if 7 <= sleep_time <= 8 else 20 if 6 <= sleep_time <= 9 else 10
    score += 30 if exercise_time >= 1.0 else 20 if exercise_time >= 0.5 else 5
    score += 40 if steps >= 10000 else 30 if steps >= 7000 else 15 if steps >= 4000 else 5
    #3.요약정보 대시보드
    st.subheader(f" {name}님의 건강 분석 결과 안내입니다.")
    col1 ,col2 ,col3 = st.columns(3)
    with col1 : 
        st.metric(label="BMI 지수" , value=f"{bmi:.2f}" ,delta=bmi_status, delta_color="inverse" if bmi_status in ["과체중","비만"] else "normal")
    with col2 : 
        st.metric(label="종합 건강 점수"  , value=f"{score} / 100점")
    with col3 : 
        status_text ="우수" if score >= 80 else "개선필요" 
        st.metric(label="생활 습관 등급"  , value=status_text)

    st.sidebar.markdown("---------------------")

    #3. 맞춤형 조언 알림 
    st.subheader(" 맞춤형 피드백 조언")
    #3.1 bmi
    if  bmi_status in ["과체중","비만"] : 
        st.warning("** 체중 관리필요 ** : 체중 관리가 필요합니다. 유산소 운동과 식단 조절을 병행하세요")
    elif  bmi_status == "저체중" :    
        st.info("** 근력 강화필요 ** : 근력 운동을 통해 근육량을 늘리고 균형 잡힌 영향을 섭취하세요")
    else : st.success ("** 정상 체중 ** : 현재 체중을 잘 유지하고 계십니다.")    
    #3.2 score
    if  score >= 80  : st.success ("** 아중 훌륭한  생활 습관을 유지하고 있습니다. 현재 상태를 잘 유지하세요.")    
    else :  
        advice_list =[] 
        if sleep_time < 6 : advice_list.append("수면 시간이 부족합니다. 하루 7시간 이상의 수면이 필요 합니다.")
        if exercise_time <0.5 : advice_list.append("운동시간이 부족합니다.일상 속 운동량을 늘려보세요")
        if steps <7000 : advice_list.append("활동량이 저조합니다. 하루 걸음 수를 점진적으로 늘려보세요")

        for advice in advice_list:
            st.error(f" * {advice} *")

    st.sidebar.markdown("---------------------")

    #3. 비교균 정보 표현 
    st.subheader(f" {name}님  vs 비교군(전체참여자) 평균 비교")

    avg_sleep = df["수면시간"].mean();
    avg_exercise = df["운동시간"].mean();
    avg_steps = df["걸음수"].mean();

    fig, axes = plt.subplots(1, 3, figsize=(12 , 4.5) , dpi=110)
    sns.set_style("whitegrid")
    
    categorise = [name ,'참여자 평균']
    colors = ['#FF6B6B' , '#A8DADC']

    #bar 두께
    bar_width = 0.20
    
    #수면시간 비교 
    axes[0].bar(categorise , [sleep_time, avg_sleep] , color=colors, width=bar_width )
    axes[0].set_title("수면 시간 비교(시간)" ,fontsize=11, fontweight='bold' ,pad=10)
    axes[0].axhline(7 , color='gray' ,  linestyle='--' ,alpha=0.7, label='avg sleep(7h)')
    axes[0].set_xlim(-0.5, 1.5)
    axes[0].legend(loc='upper right', fontsize=9)

    #운동시간 비교 
    axes[1].bar(categorise , [exercise_time, avg_exercise] , color=colors, width=bar_width)
    axes[1].set_title("운동 시간 비교(시간)" ,fontsize=11, fontweight='bold',pad=10)
    axes[1].set_xlim(-0.5, 1.5)

    #운동시간 비교 
    axes[2].bar(categorise , [steps, avg_steps] , color=colors, width=bar_width)
    axes[2].set_title("걸음 수 비교(걸음)" ,fontsize=11, fontweight='bold'  ,pad=10)
    axes[2].axhline(10000 , color='gray' ,  linestyle='--' ,alpha=0.7, label='avg step(10,000)')
    axes[2].set_xlim(-0.5, 1.5)
    axes[2].legend(loc='upper right', fontsize=9)



    plt.tight_layout()
    st.pyplot(fig)  #   streamlit 웹 페이지 matplotlib

else :
      st.info("<- 왼쪽 상단 '**<< , >>**'를 누른 후 사이드바에서 정보를 입력한 후 **[건강상태 분석하기+`]** 버튼을 눌러 주새요")
