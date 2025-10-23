from flask import Flask, render_template, request
from .scorer_main import FashionScorer

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('saiten.html')

    @app.route('/score', methods=['POST'])
    def score():
        text = request.form['text']

        # FashionScorer クラスを使うように変更
        scorer = FashionScorer(user_gender="neutral")
        # ここではダミーデータを使う（本来は画像base64とmetadata）
        dummy_metadata = {"user_locale": "ja-JP", "intended_scene": "casual"}
        result = scorer.analyze(text, dummy_metadata)  # ← analyze() に渡す

        return render_template('score.html', result=result, input_text=text)

    return app

