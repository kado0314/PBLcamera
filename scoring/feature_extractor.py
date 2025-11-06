# feature_extractor.py
import cv2
import numpy as np
import mediapipe as mp  # ▼▼▼ 追加 ▼▼▼
from typing import Dict, Any
from .rules_db import BIAS_ADJUSTMENTS

# ▼▼▼ 追加: MediaPipe Poseモデルの初期化 (起動時に1回だけ行う) ▼▼▼
mp_pose = mp.solutions.pose
# model_complexity=1 で速度と精度のバランスをとる
pose_estimator = mp_pose.Pose(
    static_image_mode=True, 
    model_complexity=1, 
    enable_segmentation=False
)
mp_drawing = mp.solutions.drawing_utils
# ▲▲▲ 追加 ▲▲▲


def preprocess_image(img: np.ndarray) -> np.ndarray:
    """色検出の安定化のため、露出補正とリサイズを行う（ダミー）"""
    return cv2.resize(img, (800, 800))

def extract_color_features(img: np.ndarray) -> Dict[str, Any]:
    """
    color_harmony のための特徴量を抽出
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    unique_colors_count = np.unique(hsv[:,:,0]).size 
    avg_saturation = np.mean(hsv[:,:,1]) / 255.0

    return {
        "hsv_hist": cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256]).flatten(),
        "primary_colors_count": min(unique_colors_count // 50, 6), # 0-6程度に正規化
        "avg_saturation_ratio": avg_saturation
    }

# ▼▼▼ 修正: この関数の中身をダミーの乱数からAIロジックに入れ替え ▼▼▼
def extract_silhouette_features(img: np.ndarray, user_gender: str) -> Dict[str, Any]:
    """
    fit_and_silhouette のための特徴量を抽出
    MediaPipe Pose Estimationモデルを使用
    """
    
    # BGR画像をRGBに変換 (MediaPipeはRGBを入力として期待するため)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 姿勢推定の実行
    results = pose_estimator.process(img_rgb)

    features = {
        "shoulder_to_height_ratio": 0.25, # デフォルト値
        "hip_to_height_ratio": 0.3,       # デフォルト値
        "is_oversized": False,
        "detection_confidence": 0.0
    }

    # ランドマーク（関節点）が検出されたか確認
    if not results.pose_landmarks:
        print("⚠️ 姿勢推定に失敗しました。ランドマークが見つかりません。")
        return features # デフォルト値を返す

    landmarks = results.pose_landmarks.landmark
    
    try:
        # 必要なランドマークの座標を取得
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]

        # 信頼度（visibility）が低い場合は計算をスキップ
        if (left_shoulder.visibility < 0.5 or right_shoulder.visibility < 0.5 or
            left_ankle.visibility < 0.5 or right_ankle.visibility < 0.5):
            print("⚠️ ランドマークの信頼度が低いため、比率の計算をスキップします。")
            return features

        # 1. 身長の推定 (足首から肩までのY座標の差として簡易的に計算)
        # Y座標は画像の上部が0, 下部が1
        avg_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
        avg_ankle_y = (left_ankle.y + right_ankle.y) / 2
        estimated_height = abs(avg_ankle_y - avg_shoulder_y)
        
        # 0除算を避ける
        if estimated_height < 0.1: # 身長の推定値が小さすぎる
             print("⚠️ 身長の推定に失敗しました。")
             return features

        # 2. 肩幅の計算 (左右の肩のX座標の差)
        # X座標は画像の左端が0, 右端が1
        shoulder_width = abs(left_shoulder.x - right_shoulder.x)
        
        # 3. 肩幅/身長 の比率を計算
        # これがシルエットの「フィット感」の根拠となる
        shoulder_ratio = shoulder_width / estimated_height
        features["shoulder_to_height_ratio"] = shoulder_ratio
        
        features["detection_confidence"] = np.mean([
            left_shoulder.visibility, right_shoulder.visibility,
            left_ankle.visibility, right_ankle.visibility
        ])

        # --- ダミーだったロジックを、本物の比率で判定 ---
        target_range = BIAS_ADJUSTMENTS.get(user_gender, BIAS_ADJUSTMENTS["neutral"])["silhouette_std_range"]
        
        # 簡易的な「肩幅が大きすぎる」判定
        if shoulder_ratio > target_range[1]: # 標準範囲の上限を超えた
            features["is_oversized"] = True
        else:
            features["is_oversized"] = False
            
    except Exception as e:
        print(f"⚠️ ランドマークの計算中にエラー: {e}")
        # エラーが発生した場合もデフォルト値を返す

    return features
# ▲▲▲ 修正 ▲▲▲
