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
    st.write("💡 **인사이트:** 탄소 절감 상위 5개 지역은 따릉이 활용도가 가장 높은 곳입니다. 이 지역들에 보관소 정비 예산을 우선 배정하는 전략이 필요합니다.")

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
    st.write("💡 **인사이트:** 연령대에 따라 선호하는 대여권이 다릅니다. 특정 연령대 타겟 마케팅을 위해 정기권/일일권 비중을 분석하는 것이 좋습니다.")

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
    st.write("💡 **인사이트:** 기온이 상승함에 따라 이용시간이 증가하는 패턴을 확인하세요. 기온이 따릉이 이용의 핵심 변수임을 알 수 있습니다.")
