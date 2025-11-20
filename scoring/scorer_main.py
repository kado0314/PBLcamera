from datetime import datetime
import json
from typing import Dict, Any
import base64
from PIL import Image
import io
import os
import google.generativeai as genai

class FashionScorer:
    """
    ファッション画像の多次元スコアリングを実行するメインクラス
    """
    MODEL_VERSION = "v1.2.0"

    def __init__(self, user_gender: str = "neutral", user_locale: str = "ja-JP"):
        self.user_gender = user_gender
        self.user_locale = user_locale
        # Gemini API モデルのロード
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def load_image(self, image_base64: str) -> bytes | None:
        """Base64文字列からJPEGバイト列に変換して返す"""
        try:
            img_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(img_bytes))

            # JPEGバイト列に変換
            img_io = io.BytesIO()
            image.save(img_io, format="JPEG")
            return img_io.getvalue()
        except Exception:
            return None

    def analyze(self, image_base64: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        response = self.model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": img_bytes}
        ])

        user_gender = metadata.get("user_gender", self.user_gender)
        intended_scene = metadata.get("intended_scene", "friends")

        # 2. プロンプト
        prompt = f"""
        あなたはプロのファッションスタイリストです。以下の画像を分析し、採点してください。
        ユーザー属性: {user_gender}, 想定シーン: {intended_scene}

        以下のJSON形式のみで出力:
        {{
            "total_score": (0-100の整数),
            "recommendation": "(一言コメント)",
            "feedback_points": ["(良い点・改善点1)", "(良い点・改善点2)", "(良い点・改善点3)"],
            "details": {{
                "color_harmony": (0-20), "fit_and_silhouette": (0-20),
                "item_coordination": (0-15), "cleanliness_material": (0-15),
                "accessories_balance": (0-10), "trendness": (0-10),
                "tpo_suitability": (0-5), "photogenic_quality": (0-5)
            }}
        }}
        """

        # 3. Gemini 推論
        try:
            response = self.model.generate_content([prompt, image])
            result_text = response.candidates[0].content[0].text
            result = json.loads(result_text)
        except Exception as e:
            return {"error": f"Gemini API error: {e}"}

        # 4. 結果を上位と揃えたフォーマットに加工
        output = {
            "overall_score": result.get("total_score", 0),
            "subscores": result.get("details", {}),
            "explanations": result.get("feedback_points", []),
            "warnings": [],
            "metadata": {
                "user_locale": metadata.get("user_locale"),
                "intended_scene": intended_scene,
                "analysis_timestamp": datetime.now().isoformat(),
                "model_version": "gemini"
            }
        }

        return output
