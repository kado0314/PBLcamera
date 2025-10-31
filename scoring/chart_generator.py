import matplotlib.pyplot as plt
import numpy as np
import io, base64, matplotlib

def generate_radar_chart(aspect_scores):
    """六角形レーダーチャートをBase64画像として返す（日本語ラベル対応）"""
    if not aspect_scores:
        return None

    # 日本語フォント設定
    matplotlib.rcParams['font.family'] = 'IPAPGothic'

    # 英語キーから日本語ラベルへの変換
    label_map = {
        'color_harmony': '色の調和',
        'fit_and_silhouette': 'シルエット・フィット感',
        'item_coordination': 'アイテムの組み合わせ',
        'cleanliness_material': '清潔感・素材感',
        'accessories_balance': '小物のバランス',
        'trendness': 'トレンド感',
        'tpo_suitability': 'TPO（場面）適合度',
        'photogenic_quality': '写真映え'
    }

    # ラベルを日本語に変換
    labels = [label_map.get(key, key) for key in scores.keys()]

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
