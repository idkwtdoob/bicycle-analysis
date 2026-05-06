import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="따릉이 이용 데이터 대시보드", layout="wide")
st.title("🚲 서울시 따릉이 데이터 분석 대시보드")

# 2. DB 연결 및 오류 처리
DB_NAME = "bicycle.db"

def get_data(query):
    if not os.path.exists(DB_NAME):
        st.error(f"⚠️ 데이터베이스 파일 '{DB_NAME}'을 찾을 수 없습니다!")
        return None
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 3. 차트 1: 자치구별 탄소절감량 (상위 5개)
st.header("1. 자치구별 탄소절감량 (Top 5)")
# [수정] ORDER BY 끝에 LIMIT 5를 추가했습니다!
query1 = """
SELECT d."자치구", SUM(i."탄소량") AS "탄소절감량"
FROM "이용정보" i
JOIN "대여소" d ON i."대여소번호" = d."대여소번호"
GROUP BY d."자치구"
ORDER BY "탄소절감량" DESC
LIMIT 5;
"""
df1 = get_data(query1)
if df1 is not None:
    fig1 = px.bar(df1, x="탄소절감량", y="자치구", orientation='h', color="탄소절감량", title="탄소절감량 상위 5개 자치구")
    # 그래프를 내림차순 정렬해서 보여주기 위해 카테고리 순서 설정
    fig1.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig1, use_container_width=True)
    st.write("💡 **인사이트:** 강서구·영등포구·송파구가 탄소절감량 상위권을 차지하며, 상위 3개 자치구와 마포구·노원구 간 격차가 뚜렷하게 나타나 탄소절감 효과가 일부 지역에 집중되어 있고, 이는 해당 지역의 자전거 이용량이나 이동거리, 생활·교통 수요가 높을 가능성을 보여준다.")

# 4. 차트 2: 연령별 대여구분코드
st.header("2. 연령별 대여 형태(비율)")
query2 = """
SELECT 연령대코드, 대여구분코드, COUNT(*) AS 이용건수
FROM 이용정보
GROUP BY 연령대코드, 대여구분코드
ORDER BY 연령대코드 ASC, 이용건수 DESC;
"""
df2 = get_data(query2)
if df2 is not None:
    fig2 = px.bar(df2, x="연령대코드", y="이용건수", color="대여구분코드", title="연령대별 대여구분 비중", barmode="stack")
    st.plotly_chart(fig2, use_container_width=True)
    st.write("💡 **인사이트:** 따릉이 이용은 20~40대를 중심으로 정기권과 일일권 이용이 대부분을 차지하며, 연령대가 높아질수록 이용건수가 감소하는 반면, 10대 이하에서는 가족권 이용이 상대적으로 두드러지고 기타 집단에서는 비회원 일일권 비중이 크게 나타난다.")
# 5. 차트 3: 기온과 이용시간의 상관관계
st.header("3. 기온에 따른 따릉이 이용시간")
query3 = """
SELECT g."평균기온", SUM(i."이용시간") AS "총이용시간"
FROM "이용정보" i
JOIN "기온" g ON SUBSTR(i."대여일자", 1, 6) = g."년월"
GROUP BY g."평균기온"
ORDER BY g."평균기온" ASC;
"""
df3 = get_data(query3)
if df3 is not None:
    # 이제 statsmodels가 설치되었으므로 에러 없이 잘 작동할 거예요!
    fig3 = px.scatter(df3, x="평균기온", y="총이용시간", trendline="ols", title="기온별 이용시간 상관관계 분석")
    st.plotly_chart(fig3, use_container_width=True)
    st.write("💡 **인사이트:** 이 그래프에서는 평균기온이 높아질수록 따릉이 총 이용시간이 전반적으로 증가하는 양의 상관관계가 나타나지만, 가장 높은 기온대보다 20도 중반대에서 이용시간이 가장 높게 나타난다.")