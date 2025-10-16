from flask import Blueprint, render_template

detect_bp = Blueprint(
    "detect",
    __name__,
    template_folder="templates",
    static_folder="static"
)

@detect_bp.route("/detect")
def detect_index():
    return render_template("index.html")
