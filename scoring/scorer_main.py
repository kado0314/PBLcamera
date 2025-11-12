# scorer_main.py
from datetime import datetime
import json
from typing import Dict, List, Any
import numpy as np
import cv2
import base64
from .rules_db import SCORE_WEIGHTS, BIAS_ADJUSTMENTS, TPO_RULES
from .feature_extractor import (
    preprocess_image, 
    extract_color_features, 
    extract_silhouette_features
)

class FashionScorer:
    """
    ファッション画像の多次元スコアリングを実行するメインクラス
    """
    MODEL_VERSION = "v1.2.0"

    def __init__(self, user_gender: str = "neutral", user_locale: str = "ja-JP"):
        self.user_gender = user_gender
        self.user_locale = user_locale
        # ここにCNNモデルやDB接続などをロード

    def load_image_from_base64(self, image_base64: str) -> np.ndarray or None:
        """Base64文字列からOpenCV形式の画像を読み込む"""
        try:
            img_bytes = base64.b64decode(image_base64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            # print(f"Error loading image: {e}")
            return None

    # --- サブスコア計算メソッド ---
    
    def _score_color_harmony(self, color_features: Dict[str, Any]) -> tuple[float, List[str]]:
        """色の調和を採点（ウェイト最大20点）"""
        score = 0.0
        explanations = []

        # 1. 色の多様性評価 (最大10点)
        max_colors = 4
        primary_colors_count = color_features["primary_colors_count"]
        if primary_colors_count <= max_colors:
            score += 10 * (1 - (primary_colors_count / max_colors * 0.5))
            explanations.append(f"色のトーンが統一されており、主要色は{primary_colors_count}色以下でまとまりがある。")
        else:
            score += 3 # 最低点
            explanations.append(f"主要色が{primary_colors_count}色以上検出され、配色がやや雑然としている。→ 主要色を4色以下に抑えると改善。")

        # 2. 彩度の一貫性評価 (最大10点)
        avg_saturation = color_features["avg_saturation_ratio"]
        if 0.2 < avg_saturation < 0.6: # 一般的な「おしゃれ」とされる範囲
            score += 10
            explanations.append("彩度が中程度で、派手すぎず地味すぎないバランス。")
        elif avg_saturation <= 0.2:
            score += 5
            explanations.append("彩度が低く、モノトーンに近いシックなトーン。→ 明るい差し色を1点加えるとアクセントになる。")
        else:
            score += 3
            explanations.append("彩度が高すぎ、全体的に派手な印象。→ 全体のトーンを落ち着かせると改善。")

        # 最終スコアを20点満点に正規化
        return round(min(score, SCORE_WEIGHTS["color_harmony"]), 1), explanations

    def _score_fit_and_silhouette(self, silhouette_features: Dict[str, Any]) -> tuple[float, List[str], List[str]]:
        """サイズ感・シルエットを採点（ウェイト最大20点）"""
        score = 0.0
        explanations = []
        warnings = []
        max_score = SCORE_WEIGHTS["fit_and_silhouette"]

        # 1. サイズのフィット評価 (最大15点)
        if silhouette_features.get("is_oversized"):
            score = max(0, max_score - 10.0) # 大幅減点
            explanations.append("ジャケットの肩幅推定値が大きく、体型とバランスが崩れている。→ 1サイズ小さいものを試すと改善。")
        else:
            score += 15.0
            explanations.append("服のフィット感が良く、プロポーションが整っている。")
            
        # 2. プロポーションバランス評価 (最大5点)
        if silhouette_features.get("jacket_fit_score", 0) > 0.8:
            score += 5.0
            explanations.append("上半身と下半身のバランスが良好。")
        else:
            warnings.append("人体検出の精度が不確実なため、シルエット評価に若干のブレが生じる可能性あり。")

        return round(min(score, max_score), 1), explanations, warnings

    def _score_other_subscores(self, subscores: Dict[str, float]) -> Dict[str, float]:
        """その他のサブスコアを簡易的にシミュレーション"""
        remaining_scores = {}
        for key, max_val in SCORE_WEIGHTS.items():
            if key not in subscores:
                # 満点の70%〜90%の間でランダムに点数を振る
                remaining_scores[key] = round(max_val * np.random.uniform(0.7, 0.9), 1)
        return remaining_scores

    # --- メイン実行メソッド ---

    def analyze(self, image_base64: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """画像とメタデータを受け取り、全スコアを計算してJSON形式で返す"""
        
        # 1. 入力処理と前処理
        img = self.load_image_from_base64(image_base64)
        if img is None:
            return {"error": "Invalid image data."}

        max_size = 200  # ← 400→200 に
        h, w = img.shape[:2]
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        
        preprocessed_img = preprocess_image(img)
        
        # 2. 特徴量抽出
        user_gender = metadata.get("user_gender", "neutral")
        
        color_features = extract_color_features(preprocessed_img)
        silhouette_features = extract_silhouette_features(preprocessed_img, user_gender)
        # item_features = extract_item_features(...)
        
        # 3. サブスコア計算と説明文・警告文の収集
        all_explanations: List[str] = []
        all_warnings: List[str] = []
        subscores: Dict[str, float] = {}

        # a. color_harmony (20点)
        score_c, exp_c = self._score_color_harmony(color_features)
        subscores["color_harmony"] = score_c
        all_explanations.extend(exp_c)
        
        # b. fit_and_silhouette (20点)
        score_f, exp_f, warn_f = self._score_fit_and_silhouette(silhouette_features)
        subscores["fit_and_silhouette"] = score_f
        all_explanations.extend(exp_f)
        all_warnings.extend(warn_f)

        # c. その他のサブスコア (残りの60点) - シミュレーション
        subscores.update(self._score_other_subscores(subscores))

        # 4. 総合点の計算
        overall_score = sum(subscores.values())

        # 5. 出力JSONの整形
        output = {
            "overall_score": round(overall_score, 1),
            "subscores": subscores,
            "explanations": all_explanations,
            "warnings": all_warnings,
            "metadata": {
                "user_locale": metadata.get("user_locale"),
                "intended_scene": metadata.get("intended_scene"),
                "analysis_timestamp": datetime.now().isoformat(),
                "model_version": self.MODEL_VERSION
            }
        }

        # UI上の注意文（必須仕様）
        output["ui_messages"] = [
            "このスコアは 日本文化圏で一般的に評価されやすいファッション基準 に基づいています。",
            f"選択した性別（{user_gender}）によって、標準とするシルエットやコーディネートの基準が異なります。",
            "写真映り（光、背景、画質、角度）によりスコアが変動する可能性があります。"
        ]

        return output

# --- 5. 実行シミュレーション ---
if __name__ == "__main__":
    # 依存ライブラリのチェック
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("必要なライブラリが見つかりません。以下を実行してください：")
        print("pip install opencv-python numpy")
        exit()

    # 簡易的なテスト用画像ファイルを作成 (OpenCVで生成)
    dummy_img = np.zeros((200, 200, 3), dtype=np.uint8)
    dummy_img[50:150, 50:150] = [20, 100, 200] # BGRで少し鮮やかな色
    
    # 画像をBase64に変換してAPIリクエストをシミュレーション
    _, buffer = cv2.imencode('.jpg', dummy_img)
    image_base64_string = base64.b64encode(buffer).decode('utf-8')

    # APIリクエストのメタデータ
    test_metadata = {
        "user_locale": "ja-JP",
        "intended_scene": "date",
        "user_gender": "male"
    }

    scorer = FashionScorer(user_gender=test_metadata["user_gender"])
    result = scorer.analyze(image_base64_string, test_metadata)

    print("=" * 40)
    print("=== ファッション採点AI (シミュレーション結果) ===")
    print("=" * 40)
    print(json.dumps(result, indent=2, ensure_ascii=False))




