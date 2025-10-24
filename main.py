from flask import Flask, render_template

app = Flask(__name__, template_folder='scoring/templates')

@app.route('/')
def index():
    # プロジェクト直下の index.html を表示
    return render_template('../index.html')

@app.route('/scoring')
def scoring():
    # scoring/templates/saiten.html を表示
    return render_template('saiten.html')

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
