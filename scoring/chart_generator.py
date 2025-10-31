@scoring_bp.route("/saiten", methods=["POST"])
def saiten():
    image_file = request.files.get("image_file")
    if not image_file:
        return render_template("saiten.html", score=None, feedback=["画像がアップロードされていません。"])

    # 画像をBase64化
    image_data = base64.b64encode(image_file.read()).decode("utf-8")
    scorer = FashionScorer(user_gender="neutral")
    result = scorer.analyze(image_data, {"user_locale": "ja-JP", "intended_scene": "date"})

    # --- subscores を安全に取得 ---
    aspect_scores = result.get("subscores", None)
    if not aspect_scores:
        print("⚠️ subscores が見つかりません。結果:", result)
        aspect_scores = {
            "color_harmony": 0,
            "fit_and_silhouette": 0,
            "item_coordination": 0,
            "cleanliness_material": 0,
            "accessories_balance": 0,
            "trendness": 0,
            "tpo_suitability": 0,
            "photogenic_quality": 0
        }

    radar_chart_data = generate_radar_chart(aspect_scores)

    return render_template(
        "saiten.html",
        uploaded_image_data=f"data:image/png;base64,{image_data}",
        score=result.get("overall_score", "N/A"),
        recommendation="あなたのコーディネートをさらに引き立てるポイントがあります！",
        feedback=result.get("explanations", ["詳細な説明はありません。"]),
        radar_chart_data=radar_chart_data
    )
