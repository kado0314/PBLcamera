# feature_extractor.py
import cv2
import numpy as np
from typing import Dict, Any
from rules_db import BIAS_ADJUSTMENTS


def preprocess_image(img: np.ndarray) -> np.ndarray:
    """色検出の安定化のため、露出補正とリサイズを行う（ダミー）"""
    # 本格実装時には、照明推定やホワイトバランス補正を行います
    return cv2.resize(img, (800, 800))

def extract_color_features(img: np.ndarray) -> Dict[str, Any]:
    """
    color_harmony のための特徴量を抽出
    指標: 色相関係、明度/彩度の一貫性（簡易ヒストグラムベース）
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 簡易クラスタリングのシミュレーション
    unique_colors_count = np.unique(hsv[:,:,0]).size 
    avg_saturation = np.mean(hsv[:,:,1]) / 255.0

    return {
        "hsv_hist": cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256]).flatten(),
        "primary_colors_count": min(unique_colors_count // 50, 6), # 0-6程度に正規化
        "avg_saturation_ratio": avg_saturation
    }

def extract_silhouette_features(img: np.ndarray, user_gender: str) -> Dict[str, Any]:
    """
    fit_and_silhouette のための特徴量を抽出
    **本来はここでPose Estimationモデルを動かします**
    """
    # ダミーのキーポイントと比率を返す
    dummy_ratios = {
        "shoulder_to_height_ratio": np.random.uniform(0.2, 0.35),
        "jacket_fit_score": np.random.uniform(0.5, 1.0) # CNNで服のフィットを評価（シミュレーション）
    }
    
    # バイアス調整の適用例
    target_range = BIAS_ADJUSTMENTS.get(user_gender, BIAS_ADJUSTMENTS["neutral"])["silhouette_std_range"]
    
    # 簡易的な「肩幅が大きすぎる」シミュレーション
    if user_gender == "male" and dummy_ratios["shoulder_to_height_ratio"] > 0.3:
        dummy_ratios["is_oversized"] = True
    else:
        dummy_ratios["is_oversized"] = False

    return dummy_ratios

# ... 他の feature_extractor 関数 (material/texture, object_detection for accessories, etc.)
