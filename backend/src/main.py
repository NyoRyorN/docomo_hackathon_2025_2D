# backend/src/main.py
from __future__ import annotations

import importlib
import logging
import pathlib
import sys
from typing import Any, Dict, List, Optional, Union, Callable
import base64
import urllib.parse
import httpx
from database import save_init_list, fetch_info, save_generated_answer
from generater import generate_answer

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---- import path 簡易調整（src 直下モジュールを import しやすく） ----
_THIS_DIR = pathlib.Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.append(str(_THIS_DIR))

# -------- ヘルパ：遅延で関数読込（存在しなければ None かエラー） --------
async def url_to_bytes(
    url: str,
    *,
    timeout: float = 10.0,
    max_bytes: int = 8 * 1024 * 1024,  # 8MB
    require_image: bool = True,
) -> bytes:
    """
    画像URL(https://...) または data URL(data:image/png;base64,...) を bytes に変換。
    - require_image=True のとき Content-Type が image/* でないと 400 を返す
    - max_bytes を超えたら 413 を返す
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL が空です。")

    # data URL 対応
    if url.startswith("data:"):
        header, data = url.split(",", 1)
        if require_image and "image" not in header.lower():
            raise HTTPException(status_code=400, detail="data URL が画像ではありません。")
        try:
            if ";base64" in header.lower():
                content = base64.b64decode(data, validate=True)
            else:
                content = urllib.parse.unquote_to_bytes(data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"data URL のデコードに失敗しました: {e}") from e
        if len(content) > max_bytes:
            raise HTTPException(status_code=413, detail="画像サイズが大きすぎます。")
        return content

    # 通常の http(s) URL
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            async with client.stream("GET", url) as resp:
                try:
                    resp.raise_for_status()
                except httpx.HTTPStatusError as e:
                    raise HTTPException(status_code=400, detail=f"画像URLの取得に失敗しました: {e}") from e

                ctype = resp.headers.get("content-type", "")
                if require_image and "image" not in ctype.lower():
                    raise HTTPException(status_code=400, detail=f"URLは画像ではありません: {ctype or 'unknown'}")

                buf = bytearray()
                async for chunk in resp.aiter_bytes():
                    buf.extend(chunk)
                    if len(buf) > max_bytes:
                        raise HTTPException(status_code=413, detail="画像サイズが大きすぎます。")
                return bytes(buf)

    except httpx.RequestError as e:
        raise HTTPException(status_code=400, detail=f"画像URLへ接続できませんでした: {e}") from e

# =========================
#  Pydantic モデル
# =========================
class InitRequest(BaseModel):
    """init_button で送られてくる初期データをDBに保存"""
    user_id: str = Field(..., description="ユーザ識別子（必須）")
    session_id: Optional[str] = Field(None, description="セッション識別子（任意）")

    name: Optional[str] = Field(None, description="ユーザ名（任意）")
    age: Optional[str] = Field(None, description="年齢（任意、DBでは years に対応）")          # ← str に変更
    height: Optional[str] = Field(None, description="身長（任意）")                           # ← str に変更
    gender: Optional[str] = Field(None, description="性別（任意）")
    weight_ideal: Optional[str] = Field(None, description="理想体重（任意）")                # ← str に変更
    picture: Optional[str] = Field(None, description="プロフィール画像URL（任意）")


class InitResponse(BaseModel):
    ok: bool
    stored_count: int

class AnswerResponse(BaseModel):
    """生成された回答を返す"""
    ok: bool
    answer: Union[str, Dict[str, Any]] = Field(..., description="生成された回答（文字列 or 詳細辞書）")
    score_percent: Optional[str] = Field(None, description="スコア（%）")                     # ← str に変更
    improvement: Optional[str] = Field(None, description="改善点（文字列）")
    future_image_url: Optional[str] = Field(None, description="将来予測画像のURL（任意）")
    current_image_url: Optional[str] = Field(None, description="現在の画像のURL（任意）")


# =========================
#  FastAPI 初期化
# =========================
def init_main() -> FastAPI:
    app = FastAPI(
        title="Backend API",
        version="0.1.0",
        description="(1) initリスト保存 (2) 画像→過去参照→回答生成→保存→返却",
    )

    # CORS（必要に応じて絞る）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger = logging.getLogger("uvicorn.error")

    @app.get("/health", tags=["meta"])
    def health() -> dict:
        return {"status": "ok"}

    # ========= 役割 (1) init リスト保存 =========
    # DB関数は他で作る前提：存在すれば呼ぶ／無ければノーオペでOK
    @app.post("/init", response_model=InitResponse, tags=["init"])
    def store_init_list(req: InitRequest) -> InitResponse:
        try:
            save_init_list(
                user_id=req.name,
                height=req.height,
                gender=req.gender,
                years=req.age,
                individual_photo_url=req.picture
            )
            # 関数が無い場合は何もしないで成功扱い
            return InitResponse(ok=True, stored_count=1)
        except Exception as e:
            logger.exception("failed to save init list: %s", e)
            raise HTTPException(status_code=500, detail=f"failed to save init list: {e}") from e


    # ========= 役割 (2) 画像URL→過去取得→回答生成→保存→返却 =========
    @app.post("/generate-answer", response_model=AnswerResponse, tags=["generate"])
    async def generate_from_images(
        name: str = Form(..., description="ユーザ名（user_idとして利用）"),
        weight: Optional[str] = Form(None, description="体重"),                 # ← str に変更
        exercise_time: Optional[str] = Form(None, description="運動時間（分）"), # ← str に変更
        sleep_time: Optional[str] = Form(None, description="睡眠時間（時間）"),   # ← str に変更
        picture: str = Form(..., description="食事画像のURL（jpg/png等）"),
    ) -> AnswerResponse:
        try:
            user_id = name

            # (a) 過去情報（必要なら取得）

            init: Dict[str, Any] = {}
            past: Dict[str, Any] = {}

            init, past = fetch_info(user_id=user_id)

            # (b) 画像URL→バイト列（必須の食事画像 / 顔はあれば）
            meal_bytes = await url_to_bytes(picture, require_image=True)

            face_bytes = None
            face_url = init.get("individual_photo_url")
            if face_url:
                face_bytes = await url_to_bytes(face_url, require_image=True)

            # init/past から画像URLは削除（generate には渡さない想定）
            init.pop("individual_photo_url", None)
            for v in past.values():
                if isinstance(v, dict):
                    v.pop("meal_image_url", None)

            # init に直近の値を注入（すべて文字列）
            if weight is not None:
                init["weight_kg"] = weight
            if exercise_time is not None:
                init["exercise_time"] = exercise_time
            if sleep_time is not None:
                init["sleep_hour"] = sleep_time

            # (c) 回答生成（必須）

            raw_result = generate_answer(meal_bytes, face_bytes, past, init)

            # dict 以外でも壊れないように整形
            if isinstance(raw_result, dict):
                result = dict(raw_result)  # コピー
            else:
                result = {"answer": raw_result}

            # 保存関数が user_id 必須のため補完
            result.setdefault("user_id", user_id)

            # (d) 生成結果を保存（存在すれば）
            save_generated_answer(result)

            # (e) 返却（score_percent は str、answer は必須）
            return AnswerResponse(
                ok=True,
                answer=result.get("answer"),
                score_percent=result.get("score_percent"),   # ← str を想定（数値でもPydanticがstr変換）
                improvement=result.get("improvement") or result.get("improvement "),
                future_image_url=result.get("future_image_url"),
                current_image_url=face_url,
            )

        except HTTPException:
            raise
        except ModuleNotFoundError as e:
            raise HTTPException(status_code=501, detail=f"必要なモジュール/関数が未実装です: {e}") from e
        except Exception as e:
            logger.exception("generate_from_images failed: %s", e)
            raise HTTPException(status_code=500, detail=f"failed to generate answer: {e}") from e

    return app


# ASGI アプリ
main = init_main()

# ローカル実行
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:main", host="0.0.0.0", port=8000, reload=True)