"""
データベース管理（最小実装・ハッカソン用, 画像はURL保存）
作成者：関澤和希
初版：2025/09/17
更新：2025/09/18（数値はすべて str / 既存テーブルの修正は行わない）

概要
- save_init_list: 固定情報の保存（プロフィール画像はURL）
- fetch_info: プロフィール + 直近7回分ログ
- save_generated_answer: 生成結果の保存（result dict仕様）
- add_meal_log: 食事/体重/睡眠ログの追加（画像はURL）

注意
- RDS接続情報は環境変数で設定（DB_HOST, DB_USER, DB_PASSWORD, DB_NAME）
"""

import os
import pymysql

# =============================
# 接続
# =============================
def _get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db-python.cnphhi3k6w2n.ap-northeast-1.rds.amazonaws.com"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "Masters1312q"),  # 本番はSecret Manager推奨
        database=os.getenv("DB_NAME", "pythondb"),
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )

def _ensure_tables():
    """
    既存テーブルの修正は一切行わず、存在しなければ作成のみ。
    数値は全て VARCHAR で保持。
    """
    ddl_user = """
    CREATE TABLE IF NOT EXISTS user_profile (
        user_id VARCHAR(64) PRIMARY KEY,
        height VARCHAR(32) NULL,
        gender VARCHAR(16) NULL,
        years VARCHAR(32) NULL,
        individual_photo_url VARCHAR(1024) NULL,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    ddl_meal = """
    CREATE TABLE IF NOT EXISTS meal_log (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user_id VARCHAR(64) NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        meal_image_url VARCHAR(1024) NULL,
        weight_kg VARCHAR(32) NULL,
        habits TEXT NULL,
        sleep_hour VARCHAR(32) NULL,
        KEY idx_user_date (user_id, created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    ddl_gen = """
    CREATE TABLE IF NOT EXISTS generated_answers (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user_id VARCHAR(64) NOT NULL,
        answer TEXT NULL,
        score_percent VARCHAR(32) NULL,
        improvement TEXT NULL,
        future_image_url VARCHAR(1024) NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        KEY idx_user_created (user_id, created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(ddl_user)
            cur.execute(ddl_meal)
            cur.execute(ddl_gen)
    finally:
        conn.close()

# import 時に一度だけ作成（失敗しても黙殺）
try:
    _ensure_tables()
except Exception:
    pass

# =============================
# 既存インタフェース
# =============================
def save_init_list(
    user_id: str,
    height: str | None,
    gender: str | None,
    years: str | None,
    individual_photo_url: str | None = None
) -> int:
    """
    固定情報の保存（UPSERT、画像はURL）
    すべて文字列で保存
    """
    _ensure_tables()
    sql = """
    INSERT INTO user_profile (user_id, height, gender, years, individual_photo_url)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        height=VALUES(height),
        gender=VALUES(gender),
        years=VALUES(years),
        individual_photo_url=VALUES(individual_photo_url)
    """
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, height, gender, years, individual_photo_url))
        return 0
    finally:
        conn.close()

def fetch_info(user_id: str):
    """初期プロフィール + 直近7回分のログ（1日1件・最新）を返す"""
    init = fetch_init_info(user_id)
    past = fetch_past_info(user_id)
    return init, past

def fetch_init_info(user_id: str):
    _ensure_tables()
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT height, gender, years, individual_photo_url FROM user_profile WHERE user_id=%s",
                (user_id,)
            )
            row = cur.fetchone()
            if row:
                return {
                    "height": row.get("height"),                 # str | None
                    "gender": row.get("gender"),
                    "years": row.get("years"),                   # str | None
                    "individual_photo_url": row.get("individual_photo_url"),
                }
            return {"height": None, "gender": None, "years": None, "individual_photo_url": None}
    finally:
        conn.close()

def fetch_past_info(user_id: str):
    """
    直近の7回分（最新→最大7件）。数値はすべて文字列で返る。
    返却キー: "0_day_ago", "1_day_ago", ...
    """
    _ensure_tables()
    past: dict[str, dict] = {}
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_id, created_at, meal_image_url, weight_kg, habits, sleep_hour
                FROM meal_log
                WHERE user_id=%s
                ORDER BY created_at DESC
                LIMIT 7
                """,
                (user_id,)
            )
            rows = cur.fetchall()

            for i in range(7):
                if i < len(rows):
                    past[f"{i}_day_ago"] = rows[i]
                else:
                    past[f"{i}_day_ago"] = {
                        "user_id": user_id,
                        "created_at": None,
                        "meal_image_url": None,
                        "weight_kg": None,  # str|None
                        "habits": None,
                        "sleep_hour": None, # str|None
                    }
    finally:
        conn.close()
    return past

# =============================
# 生成結果（result dict 仕様）
# =============================
def save_generated_answer(result: dict) -> int:
    """
    生成結果の保存（数値は文字列で保存）
    必須: result['user_id']
    任意: result['answer'], result['score_percent'], result['improvement'] / 'improvement ', result['future_image_url']
    """
    _ensure_tables()

    user_id = result.get("user_id")
    if not user_id:
        raise ValueError("result['user_id'] は必須です。")

    answer = result.get("answer")
    score_percent = result.get("score_percent")  # そのまま文字列想定（数値でも str() で保存可）
    if score_percent is not None and not isinstance(score_percent, str):
        score_percent = str(score_percent)

    improvement = result.get("improvement") or result.get("improvement ")
    future_image_url = result.get("future_image_url")

    sql = """
    INSERT INTO generated_answers (user_id, answer, score_percent, improvement, future_image_url, created_at)
    VALUES (%s, %s, %s, %s, %s, NOW())
    """
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, answer, score_percent, improvement, future_image_url))
        return 0
    finally:
        conn.close()

# =============================
# 入力補助
# =============================
def add_meal_log(
    user_id: str,
    weight_kg: str | None = None,
    habits: str | None = None,
    sleep_hour: str | None = None,
    meal_image_url: str | None = None
) -> int:
    """食事/体重/睡眠ログを1件追加（画像はURL）"""
    _ensure_tables()
    sql = """
    INSERT INTO meal_log (user_id, meal_image_url, weight_kg, habits, sleep_hour, created_at)
    VALUES (%s, %s, %s, %s, %s, NOW())
    """
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, meal_image_url, weight_kg, habits, sleep_hour))
        return 0
    finally:
        conn.close()


# =============================
# 簡易テスト
# =============================
if __name__ == "__main__":
    uid = "test_user_str"

    # プロフィール保存（URLで, 数値はstr）
    save_init_list(uid, "171.2", "male", "24", "https://example.com/avatar.png")

    # 食事ログ（URLで, 数値はstr）
    add_meal_log(
        uid,
        weight_kg="68.4",
        habits="夜食控えめ",
        sleep_hour="6.5",
        meal_image_url="https://example.com/meal.jpg"
    )

    # 生成結果（result dict仕様, 数値はstr）
    result = {
        "user_id": uid,
        "answer": "今日の提案：たんぱく質を少し増やしましょう。",
        "score_percent": "82.0",  # ← 文字列でOK（数値でもstrにして保存）
        "improvement": "間食にヨーグルトを追加",
        "future_image_url": "https://example.com/ai_result.png"
    }
    save_generated_answer(result)

    init, past = fetch_info(uid)
    print("init:", init)
    print("past keys:", list(past.keys()))