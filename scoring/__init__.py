from flask import Blueprint, render_template, request
from scoring.scorer_main import calculate_score

# Blueprint の作成
scoring_bp = Blueprint('scoring', __name__, template_folder='templates')

@scoring_bp.route('/score', methods=['GET', 'POST'])
def style_score():
    if request.method == 'POST':
        # 仮の処理：採点
        score, feedback, recommendation, subscores = calculate_score(None)
        return render_template('score.html',
                               score=score,
                               feedback=feedback,
                               recommendation=recommendation,
                               subscores=subscores,
                               uploaded_image_data=None)
    return render_template('score.html')
