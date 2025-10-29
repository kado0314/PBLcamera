from flask import Blueprint, render_template, request
from .scorer_main import FashionScorer

# Blueprint定義
scoring_bp = Blueprint('scoring', __name__, template_folder='templates')

@scoring_bp.route('/', methods=['GET', 'POST'])
def saiten():
    score = None
    recommendation = None
    feedback = None
    uploaded_image_data = None

    if request.method == 'POST':
        text = request.form.get('text', '')
        # 画像処理がまだなら text入力を仮で使用
        scorer = FashionScorer(user_gender="neutral")
        dummy_metadata = {"user_locale": "ja-JP", "intended_scene": "casual"}
        result = scorer.analyze(text, dummy_metadata)

        score = result.get('score', None)
        recommendation = result.get('recommendation', None)
        feedback = result.get('feedback', [])

    return render_template(
        'saiten.html',
        score=score,
        recommendation=recommendation,
        feedback=feedback,
        uploaded_image_data=uploaded_image_data
    )
