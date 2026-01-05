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

# 포트 설정 (문자열인 경우 대비하여 int 처리 및 기본값 설정)
MYSQL_PORT_RW = int(os.environ.get("MYSQL_PORT_RW", 6446))
MYSQL_PORT_RO = int(os.environ.get("MYSQL_PORT_RO", 6447))

# [개선] 매번 연결을 생성하여 500 에러 및 트랜잭션 고립 문제 해결
def get_db_conn(db_name, port):
    return pymysql.connect(
        host=MYSQL_HOST,
        port=port,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4', # 한글 지원
        autocommit=True
    )

# 1️⃣ 카테고리 목록
@app.get("/apply", response_class=HTMLResponse)
def serve_apply(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

@app.get("/apply/categories")
def get_categories():
    conn = get_db_conn(MYSQL_DB_1, MYSQL_PORT_RO)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT category FROM exam_info")
            return [row["category"] for row in cursor.fetchall()]
    finally:
        conn.close()

# 2️⃣ 카테고리별 자격증 목록
@app.get("/apply/exams")
def get_exams(category: str):
    conn = get_db_conn(MYSQL_DB_1, MYSQL_PORT_RO)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT cert_name FROM exam_info WHERE category=%s", (category,))
            return [row["cert_name"] for row in cursor.fetchall()]
    finally:
        conn.close()

# 3️⃣ 신청 처리
@app.post("/apply")
def apply_exam(category: str = Form(...), exam_name: str = Form(...), name: str = Form(...), birthdate: str = Form(...)):
    conn = get_db_conn(MYSQL_DB_2, MYSQL_PORT_RW)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO candidate_info (name, birth, exam_category, exam_name) VALUES (%s, %s, %s, %s)",
                (name, birthdate, category, exam_name)
            )
    finally:
        conn.close()
    return JSONResponse({"status": "success", "category": category, "exam_name": exam_name, "name": name})

# 시험 일정 HTML 페이지
@app.get("/schedule", response_class=HTMLResponse)
def serve_schedule(request: Request):
    return templates.TemplateResponse("schedule.html", {"request": request})

# 시험 일정 데이터 조회 API
@app.get("/schedule/data")
def get_exam_schedule(category: str, exam_name: str):
    conn = get_db_conn(MYSQL_DB_1, MYSQL_PORT_RO)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT category, cert_name, regist_start_date, regist_end_date, exam_start_date, exam_end_date, result_start_date, result_end_date FROM exam_info WHERE category=%s AND cert_name=%s",
                (category, exam_name)
            )
            row = cursor.fetchone()
        if not row: 
            return JSONResponse(status_code=404, content={"error": "시험 일정 없음"})
        return {
            "registration_period": {"start": str(row["regist_start_date"]), "end": str(row["regist_end_date"])},
            "exam_time": {"start": str(row["exam_start_date"]), "end": str(row["exam_end_date"])},
            "result_date": f'{row["result_start_date"]} ~ {row["result_end_date"]}'
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        conn.close()

@app.get("/result", response_class=HTMLResponse)
def serve_result(request: Request):
    return templates.TemplateResponse("result.html", {"request": request})

@app.get("/result/data")
def get_result(category: str, exam_name: str, name: str, birth: str):
    conn = get_db_conn(MYSQL_DB_2, MYSQL_PORT_RW)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT name, exam_category, exam_name, result FROM candidate_info WHERE name=%s AND birth=%s AND exam_category=%s AND exam_name=%s",
                (name, birth, category, exam_name)
            )
            row = cursor.fetchone()
        if not row: 
            return JSONResponse(status_code=200, content={"error": "시험 이력이 없습니다."})

        # 결과 해석 (개선)
        res_val = str(row["result"]).strip() if row["result"] else ""
        msg = "합격하셨습니다." if res_val == "P" else "불합격하셨습니다." if res_val == "F" else "결과 처리 중"
        return {"name": row["name"], "category": row["exam_category"], "exam_name": row["exam_name"], "result": msg}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        conn.close()

# --- [Admin Service 추가] ---
@app.get("/admin", response_class=HTMLResponse)
def serve_admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/admin/candidates")
def search_candidates(name: str):
    conn = get_db_conn(MYSQL_DB_2, MYSQL_PORT_RW)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT candidate_id, name, birth, exam_category, exam_name, result FROM candidate_info WHERE name LIKE %s", (f"%{name}%",))
            rows = cursor.fetchall()
            for r in rows: 
                r["birth"] = str(r["birth"]) if r["birth"] else ""
            return rows
    finally:
        conn.close()

@app.post("/admin/result")
def update_result(candidate_id: int = Form(...), result: str = Form(...)):
    conn = get_db_conn(MYSQL_DB_2, MYSQL_PORT_RW)
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE candidate_info SET result = %s WHERE candidate_id = %s", (result, candidate_id))
        return JSONResponse({"status": "success"})
    finally:
        conn.close()
