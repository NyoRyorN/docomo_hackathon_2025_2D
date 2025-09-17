# backend/src/main.py
from __future__ import annotations

import importlib
import logging
import pathlib
import sys
from typing import Any, Dict, List, Optional, Union, Callable

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---- import path 簡易調整（src 直下モジュールを import しやすく） ----
_THIS_DIR = pathlib.Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.append(str(_THIS_DIR))

# -------- ヘルパ：遅延で関数読込（存在しなければ None かエラー） --------
def load_func(module_name: str, func_name: str, required: bool = False) -> Optional[Callable]:
    try:
        mod = importlib.import_module(module_name)
        fn = getattr(mod, func_name)
        if callable(fn):
            return fn
        raise AttributeError
    except Exception:
        if required:
            raise
        return None

# =========================
#  Pydantic モデル
# =========================
class InitRequest(BaseModel):
    """init_button で送られてくるリスト等をDBに保存"""
    items: List[Any] = Field(..., description="初期データのリスト（任意の構造で可）")
    user_id: Optional[str] = Field(None, description="ユーザ識別子（任意）")
    session_id: Optional[str] = Field(None, description="セッション識別子（任意）")

class InitResponse(BaseModel):
    ok: bool
    stored_count: int

class AnswerResponse(BaseModel):
    """生成された回答を返す（任意のJSONを包含できるように）"""
    answer: Union[str, Dict[str, Any]]
    meta: Optional[Dict[str, Any]] = None


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
            save_init_list = load_func("database", "save_init_list", required=False)
            if save_init_list:
                save_init_list(req.items, user_id=req.user_id, session_id=req.session_id)
            # 関数が無い場合は何もしないで成功扱い
            return InitResponse(ok=True, stored_count=len(req.items))
        except Exception as e:
            logger.exception("failed to save init list: %s", e)
            raise HTTPException(status_code=500, detail=f"failed to save init list: {e}") from e

    # ========= 役割 (2) 画像→過去取得→回答生成→保存→返却 =========
    # - fetch_past_info: あれば呼ぶ／無ければ空dict
    # - generate_answer: 必須（無ければ 501 Not Implemented）
    # - save_generated_answer: あれば呼ぶ／無ければスキップ
    @app.post("/generate-answer", response_model=AnswerResponse, tags=["generate"])
    async def generate_from_images(
        meal_image: UploadFile = File(..., description="食事画像（jpg/png等）"),
        face_image: UploadFile = File(..., description="顔画像（jpg/png等）"),
        user_id: Optional[str] = Form(None),
        session_id: Optional[str] = Form(None),
    ) -> AnswerResponse:
        try:
            meal_bytes = await meal_image.read()
            face_bytes = await face_image.read()
            if not meal_bytes or not face_bytes:
                raise HTTPException(status_code=400, detail="画像が空です。")

            # (a) 過去情報
            fetch_info = load_func("database", "fetch_past_info", required=False)
            past: Dict[str, Any] = {}
            init: list[str] = []
            if fetch_info:
                init,past = fetch_info(user_id=user_id, session_id=session_id) or {}
            

            # (b) 回答生成（必須）
            generate_answer = load_func("generater", "generate_answer", required=True)
            if not generate_answer:
                raise HTTPException(status_code=501, detail="generate_answer が未実装です。")
            result = generate_answer(meal_bytes, face_bytes, past, init)

            # result から表示用 answer を抽出
            if isinstance(result, dict) and "answer" in result:
                answer_value = result["answer"]
                answer_payload = result
            else:
                answer_value = result
                answer_payload = {"answer": result}

            # (c) 生成結果を保存（存在すれば）
            save_generated_answer = load_func("database", "save_generated_answer", required=False)
            if save_generated_answer:
                try:
                    save_generated_answer(answer_payload, user_id=user_id, session_id=session_id)
                except Exception as se:
                    logger.warning("save_generated_answer failed but continue: %s", se)

            # (d) 返却
            return AnswerResponse(
                answer=answer_value,
                meta={
                    "user_id": user_id,
                    "session_id": session_id,
                    "meal_filename": meal_image.filename,
                    "face_filename": face_image.filename,
                },
            )
        except HTTPException:
            raise
        except ModuleNotFoundError as e:
            # generate_answer が未実装など
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
