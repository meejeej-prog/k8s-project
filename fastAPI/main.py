from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import pymysql
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 환경 설정 변수 선언
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_DB_1 = os.environ.get("MYSQL_DB_1")
MYSQL_DB_2 = os.environ.get("MYSQL_DB_2")

# 쓰기 전용 DB Port 변수 선언
MYSQL_PORT_RW = int(os.environ.get("MYSQL_PORT_RW", 6446))
# 읽기 전용 DB Port 변수 선언
MYSQL_PORT_RO = int(os.environ.get("MYSQL_PORT_RO", 6447))

# DB 선언
exam_conn = pymysql.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT_RO,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB_1,
    cursorclass=pymysql.cursors.DictCursor
)

candidate_conn = pymysql.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT_RW,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB_2,
    cursorclass=pymysql.cursors.DictCursor
)

# 1️⃣ 카테고리 목록
@app.get("/apply",response_class=HTMLResponse)
def serve_apply(request: Request):
    return templates.TemplateResponse(
            "apply.html",
            {"request":request}
            )
@app.get("/apply/categories")
def get_categories():
    with exam_conn.cursor() as cursor:
        cursor.execute("SELECT DISTINCT category FROM exam_info")
        return [row["category"] for row in cursor.fetchall()]

# 2️⃣ 카테고리별 자격증 목록
@app.get("/apply/exams")
def get_exams(category: str):
    with exam_conn.cursor() as cursor:
        cursor.execute(
            "SELECT cert_name FROM exam_info WHERE category=%s",
            (category,)
        )
        return [row["cert_name"] for row in cursor.fetchall()]

# 3️⃣ 신청 처리
@app.post("/apply")
def apply_exam(
    category: str = Form(...),
    exam_name: str = Form(...),
    name: str = Form(...),
    birthdate: str = Form(...)
):
    with candidate_conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO candidate_info
            (name, birth, exam_category, exam_name)
            VALUES (%s, %s, %s, %s)
            """,
            (name, birthdate, category, exam_name)
        )
        candidate_conn.commit()

    return JSONResponse({
    "status": "success",
    "category": category,
    "exam_name": exam_name,
    "name": name,
    "birthdate": birthdate
})

# 시험 일정 HTML 페이지
@app.get("/schedule", response_class=HTMLResponse)
def serve_schedule(request: Request):
    return templates.TemplateResponse(
        "schedule.html",
        {"request": request}
    )

# 시험 일정 데이터 조회 API
@app.get("/schedule/data")
def get_exam_schedule(category: str, exam_name: str):
    try:
        with exam_conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT category, cert_name,regist_start_date, regist_end_date,
                       exam_start_date, exam_end_date,
                       result_start_date, result_end_date
                FROM exam_info
                WHERE category=%s AND cert_name=%s
                """,
                (category, exam_name)
            )
            row = cursor.fetchone()

        if not row:
            return JSONResponse(status_code=404, content={"error": "시험 일정 없음"})

        return {
            "registration_period": {
                "start": str(row["regist_start_date"]),
                "end": str(row["regist_end_date"])
            },
            "exam_time": {
                "start": str(row["exam_start_date"]),
                "end": str(row["exam_end_date"])
            },
            "result_date": f'{row["result_start_date"]} ~ {row["result_end_date"]}'
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/result", response_class=HTMLResponse)
def serve_result(request: Request):
    return templates.TemplateResponse(
        "result.html",
        {"request": request}
    )

@app.get("/result/data")
def get_result(category: str, exam_name: str, name: str, birth: str):
    try:
        with candidate_conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT name, exam_category, exam_name, result
                FROM candidate_info
                WHERE name=%s AND birth=%s AND exam_category=%s AND exam_name=%s
                """,
                (name, birth, category, exam_name)
            )
            row = cursor.fetchone()

        if not row:
            return JSONResponse(
                status_code=200,
                content={"error": "시험 이력이 없습니다."}
            )

        # 결과 해석
        result_message = "Test"
        if row["result"] == "P":
            result_message = "합격하셨습니다."
        elif row["result"] == "F":
            result_message = "불합격하셨습니다."

        return {
            "name": row["name"],
            "category": row["exam_category"],
            "exam_name": row["exam_name"],
            "result": result_message
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
