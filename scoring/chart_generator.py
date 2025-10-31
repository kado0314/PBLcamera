import matplotlib.pyplot as plt
import numpy as np
import io, base64, matplotlib

def generate_radar_chart(aspect_scores):
    """六角形レーダーチャートをBase64画像として返す（日本語ラベル対応）"""
    if not aspect_scores:
        return None

    # 日本語フォント設定
    matplotlib.rcParams['font.family'] = 'IPAPGothic'

    # 英語 → 日本語 のラベル変換マップ
    label_map = {
        "color_balance": "色のバランス",
        "style_match": "スタイルの統一感",
        "fit": "サイズ感",
        "cleanliness": "清潔感",
        "uniqueness": "個性",
        "seasonal": "季節感"
    }

    # 英語のキーを日本語に置き換え（存在しないキーはそのまま）
    labels = [label_map.get(k, k) for k in aspect_scores.keys()]
    values = list(aspect_scores.values())

    # 六角形を閉じる
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    # グラフ描画
    plt.figure(figsize=(5, 5))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, values, linewidth=2, linestyle='solid')
    ax.fill(angles, values, 'skyblue', alpha=0.4)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_title("ファッション採点レーダーチャート", fontsize=14, pad=20)

    # Base64変換
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
