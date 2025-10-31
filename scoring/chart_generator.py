import matplotlib.pyplot as plt
import numpy as np
import io, base64, matplotlib

def generate_radar_chart(aspect_scores):
    import matplotlib.pyplot as plt
    import io
    import base64
    import numpy as np

    # 日本語ラベルに対応する辞書
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

    # キーを日本語に変換
    labels = [label_map.get(key, key) for key in aspect_scores.keys()]
    values = list(aspect_scores.values())

    # 円グラフの軸設定
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color='blue', linewidth=2)
    ax.fill(angles, values, color='skyblue', alpha=0.25)

    # 日本語ラベルを表示
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10, fontname="MS Gothic")

    ax.set_yticklabels([])
    ax.set_ylim(0, 25)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return f"data:image/png;base64,{chart_base64}"
