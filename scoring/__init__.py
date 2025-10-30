import base64
import cv2
import numpy as np
from flask import Blueprint, render_template, request
from .scorer_main import FashionScorer

scoring_bp = Blueprint('scoring', __name__, template_folder='templates')

@scoring_bp.route('/', methods=['GET', 'POST'])
def saiten():
    score = None
    recommendation = None
    feedback = None
    uploaded_image_data = None

    if request.method == 'POST':
        file = request.files.get('image_file')

        if file:
            # 画像をNumPy配列として読み込み
            file_bytes = np.frombuffer(file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            # base64でブラウザ表示用に変換
            _, buffer = cv2.imencode('.jpg', img)
            uploaded_image_data = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

            # --- 🔧 analyze()用にBase64文字列を用意 ---
            image_base64 = base64.b64encode(buffer).decode('utf-8')

            # 採点処理
            scorer = FashionScorer(user_gender="neutral")
            dummy_metadata = {"user_locale": "ja-JP", "intended_scene": "casual"}
            result = scorer.analyze(image_base64, dummy_metadata)

            # --- 🔧 結果の受け取り修正 ---
            score = result.get('overall_score', None)
            recommendation = "全体的なバランスと印象を考慮した評価です。"
            feedback = result.get('explanations', [])

    return render_template(
        'saiten.html',
        score=score,
        recommendation=recommendation,
        feedback=feedback,
        uploaded_image_data=uploaded_image_data
    )
