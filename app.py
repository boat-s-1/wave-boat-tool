import streamlit as st
import pandas as pd
import numpy as np
import datetime
from streamlit_drawable_canvas import st_canvas

# 1. ページ設定（アプリの最初に1回だけ！）
st.set_page_config(page_title="競艇予想ツール", layout="centered")

# 2. データの初期化
boats = [1, 2, 3, 4, 5, 6]
boat_colors = {1: "#ffffff", 2: "#000000", 3: "#ff0000", 4: "#0000ff", 5: "#ffff00", 6: "#00ff00"}
mark_score = {"☆": 6, "◎": 5, "〇": 4, "□": 3, "△": 2, "×": 1}

# セッション状態の初期化
if "place_bias" not in st.session_state:
    st.session_state.place_bias = {}

# 3. ヘッダーと基本情報の入力（ここで place を定義する）
st.title("🚤 予想ツール")
c1, c2, c3 = st.columns(3)

with c1:
    race_date = st.date_input("日付", datetime.date.today())
with c2:
    # ここで place を定義するので、これ以降で place が使えるようになります
    place = st.selectbox("競艇場", ["蒲郡", "常滑", "浜名湖", "津", "大村", "住之江", "若松", "芦屋"])
with c3:
    race_no = st.selectbox("レース", list(range(1, 13)))

# 4. 現在の場別補正表示（place の定義より下に配置）
st.markdown("### 現在の競艇場別補正値")
if place in st.session_state.place_bias and len(st.session_state.place_bias[place]) > 0:
    recent = st.session_state.place_bias[place][-30:]
    bias = float(np.mean(recent))
    st.write(f"{place} 補正値： {bias:+.4f}")
else:
    st.write("まだデータがありません")

# --- (以下に show_rank_card 関数やタブの処理を続ける) ---

def show_rank_card(rank, boat, percent, detail=None):
    # (既存の関数コード...)
    pass

tab1, tab2, tab3, tab4 = st.tabs(["簡易版", "詳細版", "ドラッグ予想", "補正展示タイム"])

# シンプル評価ロジックを共通で使うため先に初期化
simple_percent = {b: 0 for b in boats}

with tab1:
    st.subheader("シンプル評価")
    simple_input = {}
    for b in boats:
        cols = st.columns([1, 2, 2, 2, 2])
        cols[0].markdown(f"**{b}**")
        with cols[1]: motor = st.selectbox("モーター", list(mark_score), index=3, key=f"sm{b}")
        with cols[2]: local = st.selectbox("当地", list(mark_score), index=3, key=f"sl{b}")
        with cols[3]: start = st.selectbox("スタート", list(mark_score), index=3, key=f"ss{b}")
        with cols[4]: expo = st.selectbox("展示", list(mark_score), index=3, key=f"se{b}")
        simple_input[b] = [motor, local, start, expo]

    simple_scores = {b: sum(mark_score[v] for v in simple_input[b]) for b in boats}
    total_s = sum(simple_scores.values())
    if total_s > 0:
        for b in boats: simple_percent[b] = (simple_scores[b] / total_s) * 100
    
    sorted_simple = sorted(simple_scores.items(), key=lambda x: x[1], reverse=True)
    for i, (b, s) in enumerate(sorted_simple, 1):
        show_rank_card(i, b, simple_percent[b])

with tab2:
    st.subheader("詳細入力")
    detail_data = {}
    for b in boats:
        st.write(f"**{b}号艇**")
        c = st.columns(4)
        m = c[0].number_input("モーター", 0.0, 10.0, 5.0, 0.1, key=f"dm{b}")
        l = c[1].number_input("当地勝率", 0.0, 10.0, 5.0, 0.1, key=f"dl{b}")
        s = c[2].number_input("ST", 0.05, 0.30, 0.18, 0.01, key=f"ds{b}")
        e = c[3].number_input("展示", 6.0, 8.0, 6.90, 0.01, key=f"de{b}")
        detail_data[b] = {"motor": m, "local": l, "start": s, "expo": e}

    w = st.columns(4)
    wm = w[0].slider("モーター重み", 0, 5, 2)
    wl = w[1].slider("当地重み", 0, 5, 2)
    ws = w[2].slider("ST重み", 0, 5, 2)
    we = w[3].slider("展示重み", 0, 5, 2)

    detail_scores = {b: (detail_data[b]["motor"]*wm + detail_data[b]["local"]*wl + (1/detail_data[b]["start"])*ws + (1/detail_data[b]["expo"])*we) for b in boats}
    total_d = sum(detail_scores.values())
    
    sorted_detail = sorted(detail_scores.items(), key=lambda x: x[1], reverse=True)
    for i, (b, s) in enumerate(sorted_detail, 1):
        pct = (s / total_d * 100) if total_d > 0 else 0
        show_rank_card(i, b, pct, detail=detail_data[b])

with tab3:
    st.subheader("SNS用ドラッグ予想")
    objects = []
    for i, b in enumerate(boats):
        # 簡易版の評価が高い艇を少し右（前）に出す演出
        offset = 40 if simple_percent[b] >= 20 else 0
        x, y = 60 + offset, 80 + i * 60
        
        objects.append({"type": "circle", "left": x, "top": y, "radius": 22, "fill": boat_colors[b], "stroke": "black", "strokeWidth": 2})
        objects.append({"type": "text", "left": x - 8, "top": y - 14, "text": str(b), "fontSize": 24, "fontWeight": "bold", "fill": "black" if b==1 or b==5 else "white"})

    objects.append({"type": "triangle", "left": 220, "top": 100, "width": 50, "height": 50, "fill": "#ff7abf"})

    canvas = st_canvas(
        drawing_mode="transform",
        background_color="#a0e0ff",
        initial_drawing={"version": "4.4.0", "objects": objects},
        height=500, width=360, key="canvas_drag"
    )

with tab4:
    st.subheader("補正展示タイム学習")
    # ここに学習用フォームを作成
    st.info("実際の着順とタイムを紐づけて学習します（開発中）")

