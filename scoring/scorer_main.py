from scoring.feature_extractor import extract_features
from scoring.rules_db import get_rules

def calculate_score(image):
    # 特徴を抽出
    features = extract_features(image)
    
    # ルールデータベースを取得
    rules = get_rules()
    
    # 仮のスコア計算（例）
    score = sum(features.values()) % 100
    
    feedback = ["バランスが良いです", "色の組み合わせが自然です"]
    recommendation = "次は小物を工夫してみましょう！"
    subscores = {
        "color_harmony": 80,
        "fit_and_silhouette": 70,
        "item_coordination": 75,
    }
    
    return score, feedback, recommendation, subscores
