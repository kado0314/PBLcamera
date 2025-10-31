import base64
from flask import Blueprint, render_template, request
from .scorer_main import FashionScorer
from .chart_generator import generate_radar_chart

scoring_bp = Blueprint("scoring", __name__, template_folder="templates")

@scoring_bp.route("/", methods=["GET"])
def index():
    """採点ページを表示"""
    return render_template("saiten.html")

@scoring_bp.route("/saiten", methods=["POST"])
def saiten():
    """画像を受け取り採点・レーダーチャートを生成"""
    file = request.files.get("image_file")
    if not file:
        return render_template("saiten.html", feedback=["画像がアップロードされていません。"])

    # 画像をBase64変換
    image_bytes = file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # 採点処理
    scorer = FashionScorer(user_gender="neutral")
    result = scorer.analyze(image_base64, {"user_locale": "ja-JP", "intended_scene": "casual"})
    print(result["subscores"])

    # レーダーチャート生成
    radar_chart_data = generate_radar_chart(result.get("subscores", {}))

    return render_template(
        "saiten.html",
        uploaded_image_data=f"data:image/jpeg;base64,{image_base64}",
        score=result.get("overall_score"),
        recommendation="全体的なバランスと印象を考慮した評価です。",
        feedback=result.get("explanations", []),
        radar_chart_data=radar_chart_data
    )
