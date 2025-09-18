
from __future__ import annotations

import base64
import json
import os
import time
from typing import Any, Dict, Optional

import boto3
from botocore.config import Config

# ========= 設定（環境変数で上書き可） =========
from dotenv import load_dotenv
load_dotenv()
if not os.getenv("BEDROCK_CLAUDE_MODEL_ID"):
    print("[hint] Set AWS_BEARER_TOKEN_BEDROCK to your Bedrock API key.")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")

CLAUDE_MODEL_ID = os.getenv(
    "BEDROCK_CLAUDE_MODEL_ID",
    "anthropic.claude-3-5-sonnet-20240620-v1:0"
) 

NOVA_CANVAS_MODEL_ID = os.getenv(
    "BEDROCK_NOVA_CANVAS_MODEL_ID",
    "amazon.nova-canvas-v1:0"  # 実アカウントのモデルIDに合わせて調整
)

OUTPUT_S3_BUCKET = os.getenv("OUTPUT_S3_BUCKET")  # 例: "my-generated-images"
OUTPUT_S3_PREFIX = os.getenv("OUTPUT_S3_PREFIX", "generated/")
SCORE_THRESHOLD = int(os.getenv("SCORE_THRESHOLD", "50"))  # 50%未満なら「悪い」

BR_CONFIG = Config(read_timeout=60, retries={"max_attempts": 3})

# ========= AWS クライアント =========
_bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION, config=BR_CONFIG)

_s3 = None
if OUTPUT_S3_BUCKET:
    _s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", BEDROCK_REGION))


# ========= Claude (LLM) – マルチモーダル =========
def _image_block(img_bytes: bytes, media_type: str = "image/jpeg") -> Dict[str, Any]:
    return {
        "type": "image",
        "source": {"type": "base64", "media_type": media_type, "data": base64.b64encode(img_bytes).decode("utf-8")},
    }

def _build_claude_payload(meal_image: bytes, face_image: bytes, past: Dict[str, Any], init: Any) -> Dict[str, Any]:
    # init は dict / list いずれも許容（そのままJSON文字列にして渡す）
    system = (
        "あなたは誠実なヘルスコーチです。医療的診断は行いません。"
        "必ず次のJSONだけを返してください："
        "{"
        "\"answer\":\"日本語で2〜4文の評価\","
        "\"score_percent\":整数(0〜100),"
        "\"improvement\":\"改善案を日本語で1〜2文\""
        "}"
    )
    user_text = (
        "以下の情報から食事の健全性と将来リスクを評価してください。"
        "score_percent は 0〜100 で、低いほどリスクが高いとします。"
        "\n\n[CONTEXT]\n"
        f"パーソナル情報: {json.dumps(init, ensure_ascii=False)}\n"
        f"過去情報: {json.dumps(past, ensure_ascii=False)}\n"
        "- 顔画像から敏感属性は推論しない\n"
        "- 医療診断はしない\n"
        "- 出力は指定JSONのみ\n"
    )
    return {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 800,
        "temperature": 0.3,
        "system": system,
        "messages": [{
            "role": "user",
            "content": [
                _image_block(meal_image),
                {"type": "text", "text": user_text},
                _image_block(face_image),
                {"type": "text", "text": "FACEは本人の同一性文脈のみ。敏感属性は推論しない。"}
            ]
        }]
    }

def _invoke_claude(payload: Dict[str, Any]) -> Dict[str, Any]:
    resp = _bedrock.invoke_model(
        modelId=CLAUDE_MODEL_ID,
        body=json.dumps(payload, ensure_ascii=False),
        contentType="application/json",
        accept="application/json",
    )
    data = json.loads(resp["body"].read())
    text = data.get("content", [{}])[0].get("text", "")
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and "answer" in parsed and "score_percent" in parsed:
            return parsed
    except Exception:
        pass
    # フォールバック
    return {"answer": (text or "評価を生成できませんでした。"), "score_percent": 50, "improvement": "fallback"}


# ========= Nova Canvas – “太い未来像” 生成 =========
def _invoke_nova_canvas_fat(face_image: bytes, similarity: float = 0.98) -> bytes:
    import base64, json
    b64 = base64.b64encode(face_image).decode("utf-8")

    
    
    prompt = (
     "Same person and exact same face identity.one single person only. Predict the same person in the future with extreme weight gain: very obese appearance, very round and full face, large double chin, thick neck, fuller cheeks, and a big round belly with fat around the stomach and waist. The person should be standing with a slouched posture, hunched shoulders, and a weak, low-energy stance, looking unmotivated and tired. Only one single realistic photographic image"
)


    negative = (
        "two people, multiple people, duplicate person, before and after, split image, side-by-side, collage, "
        "face replacement, different person, extra body, extra face, twin, cartoon, deformed, low quality"
    )


    prompt = ("""Generate one realistic photographic image of a single person.
Keep the same face identity and clothing as the input photo.
Depict the person with an extremely oversized physique: Really fat body and face. a very round and heavy face, extremely full cheeks, a very thick neck, broad shoulders, very thick arms and legs, and an extraordinarily enlarged round belly that dominates the body and stretches the clothing to its limit. The entire figure should appear gigantic, overwhelmingly huge, and excessively expanded in size and volume.
The person should be standing with an exaggeratedly slouched and hunched posture, with a weary, exhausted facial expression, no smile, looking lazy, unmotivated, and drained of energy."""
)







    payload = {
        "taskType": "IMAGE_VARIATION",
        "imageVariationParams": {
            "images": [b64],
            "text": prompt,
            "negativeText": negative,
            "similarityStrength": max(0.95, min(1.0, similarity)),
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "cfgScale": 6.5,
            "seed": 42
            # width/height は一旦外す（入れる場合は 16 の倍数 & 画素上限内）
        },
    }
    resp = _bedrock.invoke_model(
        modelId=NOVA_CANVAS_MODEL_ID,
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json",
    )
    print(resp)
    out = json.loads(resp["body"].read())

    # images は base64 文字列の配列
    imgs = out.get("images") or []
    
    if not imgs:
        raise RuntimeError("Nova Canvas responseに画像がありません。")
    img_b64 = imgs[0] if isinstance(imgs[0], str) else imgs[0].get("b64") or imgs[0].get("base64Data")
    if not img_b64:
        raise RuntimeError("Nova Canvas responseに画像データが見つかりません。")
    return base64.b64decode(img_b64)



def _put_to_s3_and_get_url(png_bytes: bytes) -> str:
    if not _s3 or not OUTPUT_S3_BUCKET:
        # data URL で返す
        return "data:image/png;base64," + base64.b64encode(png_bytes).decode("utf-8")
    key = OUTPUT_S3_PREFIX.rstrip("/") + f"/future-fat-{int(time.time())}.png"
    _s3.put_object(Bucket=OUTPUT_S3_BUCKET, Key=key, Body=png_bytes, ContentType="image/png")
    return f"s3://{OUTPUT_S3_BUCKET}/{key}"
import re
import pathlib

def save_data_url_image(data_url: str, out_dir: str = "backend/out", basename: str = "future-fat") -> str:
    """
    data:image/*;base64,XXXXX をローカルに保存して、保存パスを返す
    """
    m = re.match(r"^data:(image/[a-zA-Z0-9.+-]+);base64,(.+)$", data_url)
    if not m:
        raise ValueError("Unsupported data URL format")

    mime, b64 = m.groups()
    ext = { "image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp" }.get(mime, ".bin")

    out_path = pathlib.Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / f"{basename}-{int(time.time())}{ext}"

    with open(file_path, "wb") as f:
        f.write(base64.b64decode(b64))
    return str(file_path)

# ========= エクスポート: main.py から呼ぶ =========
def generate_answer(meal_image_bytes: bytes, face_image_bytes: bytes,
                    past: Dict[str, Any], init: Any) -> Dict[str, Any]:
    """
    main.py から load_func で呼ばれるエントリ。
    1) Claude で評価文＆スコア（0-100%）を生成
    2) スコア < SCORE_THRESHOLD なら Nova Canvas で “太い未来像” を生成
    返り値: {"answer": str, "score_percent": int, "future_image_url": Optional[str], "improvement": str}
    """
    # 1) 評価生成
    payload = _build_claude_payload(meal_image_bytes, face_image_bytes, past=past, init=init)
    result = _invoke_claude(payload)
    answer = result.get("answer", "")
    score_percent = int(result.get("score_percent", 50))
    improvement = result.get("improvement", "")

    # 2) 将来画像（必要なら）
    future_url = None
    if score_percent < SCORE_THRESHOLD:
        try:
            png = _invoke_nova_canvas_fat(face_image_bytes, similarity=0.98)
            future_url = _put_to_s3_and_get_url(png)
        except Exception as e:
            # 画像生成失敗時はログのみ（本関数はraiseしない設計）
            print(f"[warn] future image generation failed: {e}")

    return {
        "answer": answer,
        "score_percent": 100-int(score_percent),
        "improvement": improvement,
        "future_image_url": future_url,
    }



import pathlib
import time
import base64
import json

if __name__ == "__main__":
    # ローカルテスト用
    with open(r"C:\Users\User\Downloads\test_food.jpg", "rb") as f:
        meal_bytes = f.read()
    with open(r"C:\Users\User\Downloads\istockphoto-620988108-612x612.jpg", "rb") as f:
        face_bytes = f.read()

    res = generate_answer(meal_bytes, face_bytes, past={"example": "data"}, init=[])
    print(json.dumps(res, ensure_ascii=False, indent=2))
    
    # 生成画像の保存（data URL or S3 URI or base64）
    url = res.get("future_image_url")
    if not url:
        print("[info] 将来画像は生成されませんでした（スコアが閾値以上か、生成失敗）。")
    else:
        try:
            if url.startswith("data:image/"):
                # Data URLの場合 → 直接保存
                saved = save_data_url_image(url, out_dir="backend/out", basename="future-fat")
                print(f"[saved] future image -> {saved}")
                print(f"[url] {url[:100]}...")  # URL冒頭だけ表示
                print(2)
                output = {
                    "answer": res.get("answer"),
                    "score_percent": res.get("score_percent"),
                    "improvement": res.get("improvement"),
                }
                print(json.dumps(output, ensure_ascii=False, indent=2))

            elif url.startswith("s3://"):
                # S3パスが返ってきた場合
                print(f"[info] 画像はS3に保存されています: {url}")
                # TODO: 必要なら presigned URL 発行処理を追加

            else:
                # 素のbase64のみ返ってきた場合
                # 1. Data URLを生成（ブラウザ表示用）
                data_url = f"data:image/png;base64,{url}"
                print(f"[url] {data_url[:100]}...")  # 長いので先頭だけ出力

                # 2. PNGとして保存
                out_dir = pathlib.Path("backend/out")
                out_dir.mkdir(parents=True, exist_ok=True)
                path = out_dir / f"future-fat-{int(time.time())}.png"
                with open(path, "wb") as f:
                    f.write(base64.b64decode(url))
                print(f"[saved/raw-b64] future image -> {path}")
                print(1)

        except Exception as e:
            print(f"[warn] 画像の保存に失敗しました: {e}")
