import streamlit as st
import pandas as pd
import numpy as np
import datetime
from streamlit_drawable_canvas import st_canvas

# 1. ページ設定
st.set_page_config(page_title="競艇予想ツール Pro", layout="centered")

# 2. データの初期化
boats = [1, 2, 3, 4, 5, 6]
boat_colors = {1: "#ffffff", 2: "#000000", 3: "#ff0000", 4: "#0000ff", 5: "#ffff00", 6: "#00ff00"}
mark_score = {"☆": 6, "◎": 5, "〇": 4, "□": 3, "△": 2, "×": 1}

if "place_bias" not in st.session_state:
    st.session_state.place_bias = {}

# ---------------------------
# 関数定義
# ---------------------------
def show_rank_card(rank, boat, percent, detail=None):
    medal = ["🥇", "🥈", "🥉"]
    icon = medal[rank-1] if rank <= 3 else f"{rank}位"
    
    if percent >= 30:
        bg, shadow, badge, border = "linear-gradient(135deg,#fff1b8,#ffd700)", "0 0 18px rgba(255,215,0,0.8)", "💮 本命", "2px solid #ffb700"
    elif percent >= 20:
        bg, shadow, badge, border = "linear-gradient(135deg,#ffe6f2,#ffd1ea)", "0 0 12px rgba(255,105,180,0.4)", "✨ おすすめ", "1px solid #ffb0c4"
    else:
        bg, shadow, badge, border = "linear-gradient(135deg,#ffffff,#f2f2f2)", "0 4px 10px rgba(0,0,0,0.1)", "", "none"

    html = f"""
    <div style="border-radius:18px; padding:14px 16px; margin-bottom:12px; background:{bg}; box-shadow:{shadow}; border:{border}; color: #333333;">
        <div style="font-size:20px;font-weight:bold;">{icon}　{boat}号艇 <span style="font-size:13px;color:#ff2f92;"> {badge}</span></div>
        <div style="margin-top:6px;font-size:15px;font-weight:bold;">期待値スコア：{percent:.1f}％</div>
    """
    if detail:
        html += f"<div style='margin-top:6px;font-size:13px; color:#555;'>モーター {detail['motor']} | 当地 {detail['local']} | ST {detail['start']} | 展示 {detail['expo']}</div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------
# メイン画面
# ---------------------------
st.title("🚤 予想ツール Pro")
c1, c2, c3 = st.columns(3)

with c1:
    race_date = st.date_input("日付", datetime.date.today())
with c2:
    place = st.selectbox("競艇場", ["蒲郡", "常滑", "浜名湖", "津", "大村", "住之江", "若松", "芦屋"], key="main_place_select")
with c3:
    race_no = st.selectbox("レース", list(range(1, 13)))

tab1, tab2, tab3, tab4 = st.tabs(["簡易版", "詳細版", "ドラッグ予想", "補正展示タイム"])

# シンプル評価ロジック
simple_percent = {b: 0 for b in boats}

# ---------------------------
# Tab 1: 簡易版
# ---------------------------
with tab1:
    st.subheader("シンプル評価")
    simple_input = {}
    for b in boats:
        cols = st.columns([1, 2, 2, 2, 2])
        cols[0].markdown(f"### {b}")
        with cols[1]: motor = st.selectbox("モーター", list(mark_score), index=3, key=f"sm{b}")
        with cols[2]: local = st.selectbox("当地", list(mark_score), index=3, key=f"sl{b}")
        with cols[3]: start = st.selectbox("スタート", list(mark_score), index=3, key=f"ss{b}")
        with cols[4]: expo = st.selectbox("展示", list(mark_score), index=3, key=f"se{b}")
        simple_input[b] = [motor, local, start, expo]

    simple_scores = {b: sum(mark_score[v] for v in simple_input[b]) for b in boats}
    total_s = sum(simple_scores.values())
    if total_s > 0:
        for b in boats: simple_percent[b] = (simple_scores[b] / total_s) * 100
    
    st.markdown("---")
    sorted_simple = sorted(simple_scores.items(), key=lambda x: x[1], reverse=True)
    for i, (b, s) in enumerate(sorted_simple, 1):
        show_rank_card(i, b, simple_percent[b])

# ---------------------------
# Tab 2: 詳細版
# ---------------------------
with tab2:
    st.subheader("詳細分析")
    detail_data = {}
    for b in boats:
        st.write(f"**{b}号艇**")
        c = st.columns(4)
        m = c[0].number_input("モーター評", 0.0, 10.0, 5.0, 0.1, key=f"dm{b}")
        l = c[1].number_input("当地勝率", 0.0, 10.0, 5.0, 0.1, key=f"dl{b}")
        s = c[2].number_input("平均ST", 0.05, 0.30, 0.18, 0.01, key=f"ds{b}")
        e = c[3].number_input("展示タイム", 6.0, 8.0, 6.90, 0.01, key=f"de{b}")
        detail_data[b] = {"motor": m, "local": l, "start": s, "expo": e}

    w = st.columns(4)
    wm = w[0].slider("モーター重視", 0, 5, 2)
    wl = w[1].slider("当地重視", 0, 5, 2)
    ws = w[2].slider("ST重視", 0, 5, 2)
    we = w[3].slider("展示重視", 0, 5, 2)

    detail_scores = {b: (detail_data[b]["motor"]*wm + detail_data[b]["local"]*wl + (1/detail_data[b]["start"])*ws + (1/detail_data[b]["expo"])*we) for b in boats}
    total_d = sum(detail_scores.values())
    
    st.markdown("---")
    sorted_detail = sorted(detail_scores.items(), key=lambda x: x[1], reverse=True)
    for i, (b, s) in enumerate(sorted_detail, 1):
        pct = (s / total_d * 100) if total_d > 0 else 0
        show_rank_card(i, b, pct, detail=detail_data[b])

# ---------------------------
# Tab 3: ドラッグ予想
# ---------------------------
with tab3:
    st.subheader("SNS用ドラッグ予想")
    objects = []
    for i, b in enumerate(boats):
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

# ---------------------------
# Tab 4: 補正展示タイム (修正済み)
# ---------------------------
with tab4:
    st.subheader("補正展示タイム分析")
    
    learn_place = st.selectbox(
        "学習対象の競艇場",
        ["蒲郡","常滑","浜名湖","住之江","大村","徳山","唐津"],
        key="learn_place_final"
    )

    correct = {}
    st.markdown("### 各艇データ入力")
    for b in boats:
        with st.expander(f"{b}号艇のデータ入力"):
            c = st.columns(4)
            ex = c[0].number_input("展示タイム", 6.0, 8.0, 6.90, 0.01, key=f"cex{b}")
            st_t = c[1].number_input("直線タイム", 0.0, 10.0, 5.0, 0.01, key=f"cst{b}")
            lp = c[2].number_input("1周タイム", 30.0, 60.0, 37.0, 0.01, key=f"clp{b}")
            tr = c[3].number_input("回り足", 1, 10, 5, 1, key=f"ctr{b}")
            correct[b] = {"expo": ex, "straight": st_t, "lap": lp, "turn": tr}

    # 補正計算
    place_bias_value = 0.0
    if learn_place in st.session_state.place_bias and st.session_state.place_bias[learn_place]:
        place_bias_value = float(np.mean(st.session_state.place_bias[learn_place][-30:]))

    corrected_time = {}
    for b in boats:
        base = (correct[b]["expo"] + correct[b]["lap"] * 0.10 - correct[b]["straight"] * 0.05 - correct[b]["turn"] * 0.02)
        if b == 1: base += 0.05
        corrected_time[b] = base + place_bias_value

    st.info(f"現在の {learn_place} 補正値： `{place_bias_value:+.4f}`")

    # -----------------------
    # 比較用データフレームとスタイリング
    # -----------------------
    st.markdown("### 📊 タイム比較・分析表")
    df_data = []
    for b in boats:
        df_data.append({
            "艇": f"{b}号艇",
            "展示": correct[b]["expo"],
            "直線": correct[b]["straight"],
            "1周": correct[b]["lap"],
            "回り足": correct[b]["turn"],
            "補正タイム": round(corrected_time[b], 3)
        })
    df = pd.DataFrame(df_data)

    def highlight_ranks(column):
        if column.name in ["展示", "1周", "補正タイム"]:
            # 数値が低い（早い）方が優秀
            is_1st = column == column.min()
            is_2nd = (column == column.nsmallest(2).iloc[-1]) if len(column.unique()) > 1 else [False]*6
        else:
            # 数値が高い（パワーがある）方が優秀
            is_1st = column == column.max()
            is_2nd = (column == column.nlargest(2).iloc[-1]) if len(column.unique()) > 1 else [False]*6
            
        styles = []
        for v1, v2 in zip(is_1st, is_2nd):
            if v1:
                styles.append('background-color: #ffcccc; color: #cc0000; font-weight: bold;') # 1位: 赤
            elif v2:
                styles.append('background-color: #fff9c4; color: #827717; font-weight: bold;') # 2位: 黄
            else:
                styles.append('')
        return styles

    st.dataframe(
        df.style.apply(highlight_ranks, subset=["展示", "直線", "1周", "回り足", "補正タイム"]),
        use_container_width=True, hide_index=True
    )
    st.caption("💡 赤：1位、黄：2位（タイムは低値を、評価値は高値を評価）")

    st.markdown("---")
    st.markdown("### 実際の着順を入力")
    result_order = {}
    cols = st.columns(6)
    for i, b in enumerate(boats):
        result_order[b] = cols[i].number_input(f"{b}着は？", 1, 6, b, key=f"act_{b}")

    if st.button("この結果を学習に追加"):
        avg_val = np.mean(list(corrected_time.values()))
        if learn_place not in st.session_state.place_bias:
            st.session_state.place_bias[learn_place] = []
        for b in boats:
            diff = corrected_time[b] - avg_val
            st.session_state.place_bias[learn_place].append(diff)
        st.success(f"{learn_place} の学習データを更新しました！")
