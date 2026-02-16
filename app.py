import streamlit as st
import pandas as pd
import numpy as np
import datetime

# -----------------------
# 初期化
# -----------------------
if "place_bias" not in st.session_state:
        st.session_state.place_bias = {}

# -----------------------
# 競艇場選択
# -----------------------
place = st.selectbox(
        "競艇場",
        ["蒲郡","常滑","浜名湖","住之江","大村","徳山","唐津"]
    )

# -----------------------
# 着順入力
 # -----------------------
st.markdown("### 実際の着順を入力（1〜6）")

    result = {}
    cols = st.columns(6)

    for i,b in enumerate(boats):
        with cols[i]:
            result[b] = st.number_input(
                f"{b}号艇",
                1, 6, b,
                key=f"res_{b}"
            )

# -----------------------
# 保存ボタン
# -----------------------
if st.button("このレース結果を補正学習に追加"):

        avg = np.mean(list(corrected_time.values()))

        if place not in st.session_state.place_bias:
            st.session_state.place_bias[place] = []

        for b in boats:
            diff = corrected_time[b] - avg
            st.session_state.place_bias[place].append(diff)

        st.success("補正データを保存しました")

# -----------------------
# 現在の場別補正表示
# -----------------------
st.markdown("### 現在の競艇場別補正値（直近30件平均）")

    if place in st.session_state.place_bias and len(st.session_state.place_bias[place]) > 0:

        recent = st.session_state.place_bias[place][-30:]
        bias = float(np.mean(recent))

        st.write(f"{place} 補正値： {bias:+.4f}")

    else:
        st.write("まだデータがありません")

# ---------------------------
# ページ設定
# ---------------------------
st.set_page_config(page_title="競艇予想ツール", layout="centered")

boats = [1,2,3,4,5,6]
boat_colors = {1:"#ffffff",2:"#000000",3:"#ff0000",4:"#0000ff",5:"#ffff00",6:"#00ff00"}
mark_score = {"☆":6,"◎":5,"〇":4,"□":3,"△":2,"×":1}

# ===============================
# カード表示関数
# ===============================
def show_rank_card(rank, boat, percent, detail=None):
    medal = ["🥇","🥈","🥉"]
    icon = medal[rank-1] if rank<=3 else f"{rank}位"

    # 本命・おすすめ枠
    if percent >= 30:
        bg = "linear-gradient(135deg,#fff1b8,#ffd700)"  # 金色 本命
        shadow = "0 0 18px rgba(255,215,0,0.8)"
        badge = "💮 本命"
        border = "2px solid #ffb700"
    elif percent >= 20:
        bg = "linear-gradient(135deg,#ffe6f2,#ffd1ea)"  # 薄ピンク おすすめ
        shadow = "0 0 12px rgba(255,105,180,0.4)"
        badge = "✨ おすすめ"
        border = "1px solid #ffb0c4"
    else:
        bg = "linear-gradient(135deg,#ffffff,#f2f2f2)"
        shadow = "0 4px 10px rgba(0,0,0,0.1)"
        badge = ""
        border = "none"

    html = f"""
<div style="
border-radius:18px;
padding:14px 16px;
margin-bottom:12px;
background:{bg};
box-shadow:{shadow};
border:{border};
">

<div style="font-size:20px;font-weight:bold;">
{icon}　{boat}号艇
<span style="font-size:13px;color:#ff2f92;"> {badge}</span>
</div>

<div style="margin-top:6px;font-size:15px;font-weight:bold;">
おすすめ度：{percent:.0f}％
</div>
"""

    if detail is not None:
        html += f"""
<div style="margin-top:6px;font-size:14px;">
モーター {detail['motor']}｜
当地 {detail['local']}｜
ST {detail['start']}｜
展示 {detail['expo']}
</div>
"""

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

# ---------------------------
# ヘッダ
# ---------------------------
st.title("🚤 予想ツール")
c1,c2,c3 = st.columns(3)

with c1:
    race_date = st.date_input("日付", datetime.date.today())
with c2:
    place = st.selectbox("競艇場", ["蒲郡","常滑","浜名湖","津","大村","住之江","若松","芦屋"])
with c3:
    race_no = st.selectbox("レース", list(range(1,13)))

st.caption(f"{race_date}　{place} {race_no}R")
tab1, tab2, tab3, tab4 = st.tabs([
    "簡易版",
    "詳細版",
    "ドラッグ予想",
    "補正展示タイム"
])
with tab4:
    st.subheader("結果入力 → 競艇場別補正を学習")

    import numpy as np
# ===============================
# 簡易版
# ===============================
with tab1:

    st.subheader("シンプル評価（☆◎〇□△×）")
    simple = {}

    for b in boats:
        st.markdown(f"### {b}号艇")
        c1, c2, c3, c4 = st.columns(4)
        simple[b] = {}

        with c1:
            simple[b]["motor"] = st.selectbox("モーター", list(mark_score), index=3, key=f"sm{b}")
        with c2:
            simple[b]["local"] = st.selectbox("当地", list(mark_score), index=3, key=f"sl{b}")
        with c3:
            simple[b]["start"] = st.selectbox("スタート", list(mark_score), index=3, key=f"ss{b}")
        with c4:
            simple[b]["expo"] = st.selectbox("展示", list(mark_score), index=3, key=f"se{b}")

    # スコア計算
    simple_scores = {
        b: sum(mark_score[v] for v in simple[b].values())
        for b in boats
    }

    total_score = sum(simple_scores.values())

    # ★← これがドラッグ用に使う％
    simple_percent = {}
    for b, s in simple_scores.items():
        if total_score == 0:
            simple_percent[b] = 0
        else:
            simple_percent[b] = s / total_score * 100

    rank = sorted(simple_scores.items(), key=lambda x: x[1], reverse=True)

    st.subheader("シンプルランキング")

    for i, (b, s) in enumerate(rank, 1):
        percent = simple_percent[b]
        show_rank_card(i, b, percent)

# ===============================
# 詳細版
# ===============================
with tab2:

    st.subheader("詳細入力")
    detail = {}

    for b in boats:
        st.markdown(f"### {b}号艇")
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            motor = st.number_input("モーター", 0.0, 10.0, 5.0, 0.1, key=f"dm{b}")
        with c2:
            local = st.number_input("当地勝率", 0.0, 10.0, 5.0, 0.1, key=f"dl{b}")
        with c3:
            start = st.number_input("ST", 0.05, 0.30, 0.18, 0.01, key=f"ds{b}")
        with c4:
            expo = st.number_input("展示", 6.0, 8.0, 6.90, 0.01, key=f"de{b}")

        detail[b] = {
            "motor": motor,
            "local": local,
            "start": start,
            "expo": expo
        }

    st.markdown("### 重み設定")
    w1, w2, w3, w4 = st.columns(4)
    with w1: wm = st.slider("モーター重視", 0, 5, 2)
    with w2: wl = st.slider("当地重視", 0, 5, 2)
    with w3: ws = st.slider("ST重視", 0, 5, 2)
    with w4: we = st.slider("展示重視", 0, 5, 2)

    # スコア
    detail_scores = {}
    for b in boats:
        detail_scores[b] = (
            detail[b]["motor"] * wm +
            detail[b]["local"] * wl +
            (1 / detail[b]["start"]) * ws +
            (1 / detail[b]["expo"]) * we
        )

    # ★簡易版と同じ：合計で％化
    total_score = sum(detail_scores.values())

    detail_percent = {}
    for b, s in detail_scores.items():
        if total_score == 0:
            detail_percent[b] = 0
        else:
            detail_percent[b] = s / total_score * 100

    rank_detail = sorted(detail_scores.items(), key=lambda x: x[1], reverse=True)

    st.subheader("詳細ランキング")

    for i, (b, s) in enumerate(rank_detail, 1):
        percent = detail_percent[b]

        show_rank_card(
            i,
            b,
            percent,
            detail=detail[b]
        )

# ===============================
# ドラッグ予想
# ===============================
with tab3:

    st.subheader("SNS用ドラッグ予想")

    base_mode = st.radio(
        "初期並び",
        ["シンプルランキング","詳細ランキング","自由"],
        horizontal=True
    )

    objects = []

    # ① 艇は 1→6 固定で縦に並べる
    for i, b in enumerate(boats):

        base_x = 60

        if simple_percent.get(b, 0) >= 17:
            x = base_x + 40
        else:
            x = base_x

        y = 80 + i * 60

        objects.append({
            "type": "circle",
            "left": x,
            "top": y,
            "radius": 22,
            "fill": boat_colors[b],
            "stroke": "black",
            "strokeWidth": 2
        })

        objects.append({
            "type": "text",
            "left": x - 8,
            "top": y - 14,
            "text": str(b),
            "fontSize": 24,
            "fontWeight": "bold",
            "stroke": "white",
            "strokeWidth": 1.5,
            "fill": "black"
        })

    # ② ターンマーク（ピンクの△）は1個だけ追加
    objects.append({
        "type": "triangle",
        "left": 170,
        "top": 60,          # ← 少し下げて〇より少し上くらい
        "width": 40,
        "height": 40,
        "fill": "#ff7abf",
        "stroke": "#ff3fa4",
        "strokeWidth": 2
    })

    init_draw = {
        "version": "4.4.0",
        "objects": objects
    }

    canvas = st_canvas(
        drawing_mode="transform",
        background_color="#a0e0ff",
        initial_drawing=init_draw,
        height=500,  
        width=360,
        update_streamlit=True,
        key="canvas_drag"
    )

# ===============================
# 補正展示タイム
# ===============================
with tab4:

    st.subheader("補正展示タイム")

    # -----------------------
    # 学習データ初期化
    # -----------------------
    if "place_bias" not in st.session_state:
        st.session_state.place_bias = {}

    correct = {}

    st.markdown("### 各艇データ入力")

    for b in boats:

        st.markdown(f"#### {b}号艇")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            expo = st.number_input("展示タイム", 6.0, 8.0, 6.90, 0.01, key=f"cex{b}")
        with c2:
            straight = st.number_input("直線タイム", 0.0, 10.0, 5.0, 0.01, key=f"cst{b}")
        with c3:
            lap = st.number_input("1周タイム", 30.0, 60.0, 37.0, 0.01, key=f"clp{b}")
        with c4:
            turn = st.number_input("回り足", 1, 10, 5, 1, key=f"ctr{b}")

        correct[b] = {
            "expo": expo,
            "straight": straight,
            "lap": lap,
            "turn": turn
        }

    # -------------------------
    # 場別補正値
    # -------------------------
    place_bias_value = 0.0
    if place in st.session_state.place_bias:
        recent = st.session_state.place_bias[place][-30:]
        if len(recent) > 0:
            place_bias_value = float(np.mean(recent))

    st.caption(f"※ {place} 場補正適用値：{place_bias_value:+.4f}")

    # -------------------------
    # 補正計算
    # -------------------------
    corrected_time = {}
    lap_plus_expo = {}

    for b in boats:

        base = (
            correct[b]["expo"]
            + correct[b]["lap"] * 0.10
            - correct[b]["straight"] * 0.05
            - correct[b]["turn"] * 0.02
        )

        if b == 1:
            base += 0.05

        corrected_time[b] = base + place_bias_value
        lap_plus_expo[b] = correct[b]["expo"] + correct[b]["lap"]

    # -------------------------
    # ランキング表示
    # -------------------------
    st.subheader("補正展示タイム順位")

    rank_correct = sorted(corrected_time.items(), key=lambda x: x[1])

    for i, (b, v) in enumerate(rank_correct):

        if i == 0:
            bg = "#ff4d4d"
        elif i == 1:
            bg = "#ffe066"
        else:
            bg = "#f3f3f3"

        st.markdown(
            f"""
            <div style="
                background:{bg};
                padding:10px;
                border-radius:10px;
                margin-bottom:6px;">
                <b>{i+1}位　{b}号艇</b><br>
                補正展示タイム：{v:.3f}<br>
                展示＋1周：{lap_plus_expo[b]:.2f}
            </div>
            """,
            unsafe_allow_html=True
        )

    # -------------------------
    # 学習用：着順入力
    # -------------------------
    st.markdown("### 実際の着順を入力（学習用）")

    cols = st.columns(6)
    result = {}

    for i, b in enumerate(boats):
        with cols[i]:
            result[b] = st.number_input(
                f"{b}号艇",
                1, 6, b,
                key=f"res_{b}"
            )

    if st.button("このレース結果を補正学習に追加"):

        avg = np.mean(list(corrected_time.values()))

        if place not in st.session_state.place_bias:
            st.session_state.place_bias[place] = []

        for b in boats:
            diff = corrected_time[b] - avg
            st.session_state.place_bias[place].append(diff)

        st.success("補正データを保存しました")

    # -------------------------
    # 表
    # -------------------------
    st.subheader("展示比較表（公式風）")

    rows = []
    for b in boats:
        rows.append({
            "艇": b,
            "展示": correct[b]["expo"],
            "一周": correct[b]["lap"],
            "回り足": correct[b]["turn"],
            "直線": correct[b]["straight"]
        })

    df = pd.DataFrame(rows).set_index("艇")

    def highlight_top2(s, ascending=True):

        order = s.rank(method="min", ascending=ascending)

        out = []
        for r in order:
            if r == 1:
                out.append("background-color:#ff5c5c")
            elif r == 2:
                out.append("background-color:#ffd84d")
            else:
                out.append("")
        return out

    styled = df.style \
        .apply(lambda s: highlight_top2(s, True), subset=["展示", "一周"]) \
        .apply(lambda s: highlight_top2(s, True), subset=["直線"]) \
        .apply(lambda s: highlight_top2(s, False), subset=["回り足"])

    st.dataframe(styled, use_container_width=True)
































