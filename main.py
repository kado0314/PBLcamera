from flask import Flask, render_template
from scoring import scoring_bp
from detect import detect_bp

def create_app():
    app = Flask(__name__, static_folder="static")

    # Blueprint 登録
    app.register_blueprint(scoring_bp)
    app.register_blueprint(detect_bp)

    # トップページ
    @app.route('/')
    def index():
        return render_template('index.html')

    return app


if __name__ == '__main__':
    app = create_app()
    print("アプリ起動中: http://127.0.0.1:5000/")
    app.run(debug=True)
