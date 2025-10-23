from flask import Flask, render_template

app = Flask(__name__, static_folder="static")

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print("アプリ起動中: http://127.0.0.1:5000/")
    app.run(debug=True)
