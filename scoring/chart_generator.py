import matplotlib.pyplot as plt
import numpy as np
import io, base64, matplotlib
from matplotlib import font_manager
import os

def generate_radar_chart(aspect_scores):
    # ======== 日本語フォント設定 ========
    # Render(Linux)環境では /usr/share/fonts/opentype にインストールされる
    font_paths = [
        "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",  # プロポーショナル
        "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",   # 固定幅
    ]

    font_path = next((p for p in font_paths if os.path.exists(p)), None)

    if font_path:
        font_manager.fontManager.addfont(font_path)
        matplotlib.rcParams["font.family"] = "IPAPGothic"
        print(f"✅ 日本語フォント適用: {font_path}")
    else:
        print("⚠️ IPAフォントが見つかりません。デフォルトフォントを使用します。")

    # ======== 日本語ラベル ========
    label_map = {
        'color_harmony': '色の調和',
        'fit_and_silhouette': 'シルエット・フィット感',
        'item_coordination': 'アイテムの組み合わせ',
        'cleanliness_material': '清潔感・素材感',
        'accessories_balance': '小物のバランス',
        'trendness': 'トレンド感',
        'tpo_suitability': 'TPO適合度',
        'photogenic_quality': '写真映え'
    }

    labels = [label_map.get(key, key) for key in aspect_scores.keys()]
    values = list(aspect_scores.values())
    num_vars = len(labels)

    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color='blue', linewidth=2)
    ax.fill(angles, values, color='skyblue', alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_yticklabels([])
    ax.set_ylim(0, 25)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return f"data:image/png;base64,{chart_base64}"
