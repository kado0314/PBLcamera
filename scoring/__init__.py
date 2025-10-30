import base64
import cv2
import io
import numpy as np
import matplotlib.pyplot as plt
from flask import Blueprint, render_template, request
from .scorer_main import FashionScorer

scoring_bp = Blueprint('scoring', __name__, template_folder='templates')

@scoring_bp.route('/', methods=['GET', 'POST'])
def saiten():
    score = None
    recommendation = None
    feedback = None
    uploaded_image_data = None
    radar_chart_data = None  # ←追加

    if request.method == 'POST':
        file = request.files.get('image_file')

        if file:
            # 画像をNumPy配列として読み込み
            file_bytes = np.frombuffer(file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            # base64でブラウザ表示用に変換
            _, buffer = cv2.imencode('.jpg', img)
            uploaded_image_data = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

            # --- analyze()用にBase64文字列を用意 ---
            image_base64 = base64.b64encode(buffer).decode('utf-8')

            # 採点処理
            scorer = FashionScorer(user_gender="neutral")
            dummy_metadata = {"user_locale": "ja-JP", "intended_scene": "casual"}
            result = scorer.analyze(image_base64, dummy_metadata)

            score = result.get('overall_score', None)
            recommendation = "全体的なバランスと印象を考慮した評価です。"
            feedback = result.get('explanations', [])

            # --- 🔷 レーダーチャート生成 ---
            aspect_scores = {
                "色使い": np.random.randint(50, 100),
                "清潔感": np.random.randint(50, 100),
                "季節感": np.random.randint(50, 100),
                "トレンド": np.random.randint(50, 100),
                "バランス": np.random.randint(50, 100),
                "個性": np.random.randint(50, 100),
            }

            labels = list(aspect_scores.keys())
            values = list(aspect_scores.values())
            values += values[:1]  # 六角形を閉じるために最初の値を再追加

            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
            angles += angles[:1]

            plt.figure(figsize=(5, 5))
            ax = plt.subplot(111, polar=True)
            ax.plot(angles, values, linewidth=2, linestyle='solid')
            ax.fill(angles, values, 'skyblue', alpha=0.4)
            ax.set_yticklabels([])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, fontsize=12)
            ax.set_title("ファッション採点レーダーチャート", fontsize=14, pad=20)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close()
            buf.seek(0)
            radar_chart_data = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

    return render_template(
        'saiten.html',
        score=score,
        recommendation=recommendation,
        feedback=feedback,
        uploaded_image_data=uploaded_image_data,
        radar_chart_data=radar_chart_data  # ←追加
    )
