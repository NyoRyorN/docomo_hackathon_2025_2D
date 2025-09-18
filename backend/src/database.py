"""
データベース管理（最小実装・ハッカソン用, 画像はURL保存）
作成者：関澤和希
初版：2025/09/17
更新：2025/09/18（save_generated_answerは result dict を受け取る／画像はURL）

概要
- save_init_list: 固定情報の保存（プロフィール画像はURL）
- fetch_info: プロフィール + 直近7日分ログ（各日最新1件）
- save_generated_answer: 生成結果の保存（result dict仕様）
- add_meal_log: 食事/体重/睡眠ログの追加（画像はURL）

注意
- RDS接続情報は環境変数で設定してください（DB_HOST, DB_USER, DB_PASSWORD, DB_NAME）。
- 本番では AWS Secrets Manager / IAM auth 等の利用を推奨。
"""

import os
from datetime import datetime, timedelta
import pymysql

# =============================
# 接続 & 最小オートマイグレーション
# =============================
def _get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db-python.cnphhi3k6w2n.ap-northeast-1.rds.amazonaws.com"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "Masters1312q"),  # ← 環境変数で渡す。本番はSecret Manager推奨
        database=os.getenv("DB_NAME", "pythondb"),
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )

def _ensure_tables():
    """
    - 新規作成時はURL列でテーブル生成
    - 既存にBLOB列があってもURL列を追加し、可能ならBLOB列をDROP（データ移行は別途）
    - MySQLのバージョンや権限で IF [NOT] EXISTS が使えない場合は try/except で黙殺
    """
    ddl_user = """
    CREATE TABLE IF NOT EXISTS user_profile (
        user_id VARCHAR(64) PRIMARY KEY,
        height FLOAT NULL,
        gender VARCHAR(16) NULL,
        years INT NULL,
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
        weight_kg FLOAT NULL,
        habits TEXT NULL,
        sleep_hour FLOAT NULL,
        KEY idx_user_date (user_id, created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    ddl_gen = """
    CREATE TABLE IF NOT EXISTS generated_answers (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user_id VARCHAR(64) NOT NULL,
        ration FLOAT NULL,
        answer TEXT NULL,
        generated_image_url VARCHAR(1024) NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        KEY idx_user_created (user_id, created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    # 既存テーブルの最小ALTER（URL列追加、旧BLOB列を可能ならDROP）
    alters = [
        # user_profile
        "ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS individual_photo_url VARCHAR(1024) NULL AFTER years",
        "ALTER TABLE user_profile DROP COLUMN IF EXISTS individual_photo",
        # meal_log
        "ALTER TABLE meal_log ADD COLUMN IF NOT EXISTS meal_image_url VARCHAR(1024) NULL AFTER created_at",
        "ALTER TABLE meal_log DROP COLUMN IF EXISTS meal_image",
        # generated_answers
        "ALTER TABLE generated_answers ADD COLUMN IF NOT EXISTS ration FLOAT NULL AFTER user_id",
        "ALTER TABLE generated_answers ADD COLUMN IF NOT EXISTS answer TEXT NULL AFTER ration",
        "ALTER TABLE generated_answers ADD COLUMN IF NOT EXISTS generated_image_url VARCHAR(1024) NULL AFTER answer",
        "ALTER TABLE generated_answers DROP COLUMN IF EXISTS result_text",
        "ALTER TABLE generated_answers DROP COLUMN IF EXISTS result_image",
        "ALTER TABLE generated_answers DROP COLUMN IF EXISTS result_image_url",
    ]

    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(ddl_user)
            cur.execute(ddl_meal)
            cur.execute(ddl_gen)
            for q in alters:
                try:
                    cur.execute(q)
                except Exception:
                    # 古いMySQLや権限不足等でIF NOT EXISTS/IF EXISTSが使えない場合は無視
                    pass
    finally:
        conn.close()

# モジュールimport時に一度だけ作成（失敗しても他処理に影響しない）
try:
    _ensure_tables()
except Exception:
    # 接続未設定時でも他関数で再挑戦できるよう黙殺
    pass

# =============================
# 既存インタフェース
# =============================
def save_init_list(
    user_id: str,
    height: float | None,
    gender: str | None,
    years: int | None,
    individual_photo_url: str | None = None
) -> int:
    """
    固定情報の保存（UPSERT、画像はURL）
    戻り値: 0（成功時）
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
    """
    初期プロフィール + 直近7日分のログ（1日1件・最新）を返す
    """
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
                    "height": row.get("height"),
                    "gender": row.get("gender"),
                    "years": row.get("years"),
                    "individual_photo_url": row.get("individual_photo_url"),
                }
            # 未登録時のデフォルト
            return {
                "height": None,
                "gender": None,
                "years": None,
                "individual_photo_url": None
            }
    finally:
        conn.close()

def fetch_past_info(user_id: str):
    """
    直近の7回分を返却。
    最新から順に取得し、7件未満ならあるだけ返す。
    返却形式: dict[str, dict], キーは "0_day_ago", "1_day_ago", ... とする。
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
                        "weight_kg": None,
                        "habits": None,
                        "sleep_hour": None
                    }
    finally:
        conn.close()
    return past


# =============================
# 生成結果（result dict 仕様）
# =============================
def save_generated_answer(result: dict) -> int:
    """
    生成結果の保存（result 辞書を受け取る版）
    必須: result['user_id']
    任意: result['ration'] (float), result['answer'] (str), result['generated_image'] (URL str)
    戻り値: 0（成功時）

    result = {
        "user_id": "sekizawa",   # str, 必須
        "ration": None,          # float | None
        "answer": None,          # str   | None
        "generated_image": None  # str   | None （画像URL）
    }
    """
    _ensure_tables()

    user_id = result.get("user_id")
    ration = result.get("ration")
    answer = result.get("answer")
    generated_image_url = result.get("generated_image")  # URLをそのまま保存

    if not user_id:
        raise ValueError("result['user_id'] は必須です。")

    sql = """
    INSERT INTO generated_answers (user_id, ration, answer, generated_image_url, created_at)
    VALUES (%s, %s, %s, %s, NOW())
    """
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, ration, answer, generated_image_url))
        return 0
    finally:
        conn.close()

    return 0

# =============================
# 入力補助
# =============================
def add_meal_log(
    user_id: str,
    weight_kg: float | None = None,
    habits: str | None = None,
    sleep_hour: float | None = None,
    meal_image_url: str | None = None
) -> int:
    """
    食事/体重/睡眠ログを1件追加（画像はURL）
    """
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
    uid = "test_user"

    # プロフィール保存（URLで）
    save_init_list(uid, 171.2, "male", 24, "https://example.com/avatar.png")

    # 食事ログ（URLで）
    add_meal_log(
        uid,
        weight_kg=68.4,
        habits="夜食控えめ",
        sleep_hour=6.5,
        meal_image_url="https://example.com/meal.jpg"
    )

    # 生成結果（result dict仕様）
    result = {
        "user_id": uid,
        "ration": 0.82,
        "answer": "今日の提案：たんぱく質を少し増やしましょう。",
        "generated_image": "https://example.com/ai_result.png"
    }
    save_generated_answer(result)

    init, past = fetch_info(uid)
    print("init:", init)
    print("past keys:", list(past.keys()))
