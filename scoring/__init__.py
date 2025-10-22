from flask import Flask, render_template, request
from .scorer_main import calculate_score

def create_app():
    app = Flask(__name__)

    # メインページ（フォームを表示）
    @app.route('/')
    def index():
        return render_template('score.html')

    # フォームから送られたデータを受け取って採点する
    @app.route('/score', methods=['POST'])
    def score():
        text = request.form['text']  # HTMLのフォームから送られたテキストを受け取る
        result = calculate_score(text)  # scorer_main.pyの関数を使って採点
        return render_template('score.html', result=result, input_text=text)

    return app
