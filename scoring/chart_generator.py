import matplotlib.pyplot as plt
import numpy as np
import io, base64, os
from matplotlib import font_manager

def generate_radar_chart(aspect_scores):
    """
    ファッション採点結果をレーダーチャートとして描画し、Base64画像データを返す
    """

    # ======== フォント設定 ========
    # PBLcamera/fonts/KleeOne-Regular.ttf を指定
    font_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'KleeOne-Regular.ttf')
    font_path = os.path.abspath(font_path)

    try:
        if os.path.exists(font_path):
            font_manager.fontManager.addfont(font_path)
            font_name = font_manager.FontProperties(fname=font_path).get_name()
            plt.rcParams["font.family"] = font_name
            print(f"✅ Kleeフォントを使用: {font_name}")
        else:
            print(f"⚠️ Kleeフォントが見つかりません: {font_path}")
            plt.rcParams["font.family"] = "DejaVu Sans"
    except Exception as e:
        print(f"⚠️ フォント設定エラー: {e}")
        plt.rcParams["font.family"] = "DejaVu Sans"

    # ======== ラベル（日本語） ========
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

    # ======== 六角形レーダーチャート設定 ========
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
    ax.set_title("ファッション採点レーダーチャート", fontsize=14, pad=20)

    # ======== Base64変換 ========
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return f"data:image/png;base64,{chart_base64}"
