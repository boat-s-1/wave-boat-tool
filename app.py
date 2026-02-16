import streamlit as st
import pandas as pd
import numpy as np
import datetime
from streamlit_drawable_canvas import st_canvas

# 1. ページ設定
st.set_page_config(page_title="競艇予想ツール", layout="centered")

# 2. データの初期化
boats = [1, 2, 3, 4, 5, 6]
boat_colors = {1: "#ffffff", 2: "#000000", 3: "#ff0000", 4: "#0000ff", 5: "#ffff00", 6: "#00ff00"}
mark_score = {"☆": 6, "◎": 5, "〇": 4, "□": 3, "△": 2, "×": 1}

if "place_bias" not in st.session_state:
    st.session_state.place_bias = {}

# ---------------------------
# 【重要】関数定義の復活
# ---------------------------
def show_rank_card(rank, boat, percent, detail=None):
    medal = ["🥇", "🥈", "🥉"]
    icon = medal[rank-1] if rank <= 3 else f"{rank}位"
    
    # スコアに応じた色の設定
    if percent >= 30:
        bg, shadow, badge, border = "linear-gradient(135deg,#fff1b8,#ffd700)", "0 0 18px rgba(255,215,0,0.8)", "💮 本命", "2px solid #ffb700"
    elif percent >= 20:
        bg, shadow, badge, border = "linear-gradient(135deg,#ffe6f2,#ffd1ea)", "0 0 12px rgba(255,105,180,0.4)", "✨ おすすめ", "1px solid #ffb0c4"
    else:
        bg, shadow, badge, border = "linear-gradient(135deg,#ffffff,#f2f2f2)", "0 4px 10px rgba(0,0,0,0.1)", "", "none"

    # HTMLカードの生成（テキスト色を黒で固定して視認性を確保）
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
st.title("🚤 予想ツール")
c1, c2, c3 = st.columns(3)

with c1:
    race_date = st.date_input("日付", datetime.date.today())
with c2:
    place = st.selectbox("競艇場", ["蒲郡", "常滑", "浜名湖", "津", "大村", "住之江", "若松", "芦屋"])
with c3:
    race_no = st.selectbox("レース", list(range(1, 13)))

tab1, tab2, tab3, tab4 = st.tabs(["簡易版", "詳細版", "ドラッグ予想", "補正展示タイム"])

# シンプル評価ロジックを共通で使うため先に初期化
simple_percent = {b: 0 for b in boats}

# ===============================
# 簡易版
# ===============================
with tab1:
    st.subheader("シンプル評価（☆〜×）")
    simple_input = {}
    for b in boats:
        cols = st.columns([1, 2, 2, 2, 2])
        cols[0].markdown(f"### {b}")
        with cols[1]: motor = st.selectbox("モーター", list(mark_score), index=3, key=f"sm{b}")
        with cols[2]: local = st.selectbox("当地", list(mark_score), index=3, key=f"sl{b}")
        with cols[3]: start = st.selectbox("スタート", list(mark_score), index=3, key=f"ss{b}")
        with cols[4]: expo = st.selectbox("展示", list(mark_score), index=3, key=f"se{b}")
        simple_input[b] = [motor, local, start, expo]

    # スコア計算
    simple_scores = {b: sum(mark_score[v] for v in simple_input[b]) for b in boats}
    total_s = sum(simple_scores.values())
    
    if total_s > 0:
        for b in boats: simple_percent[b] = (simple_scores[b] / total_s) * 100
    
    st.markdown("---")
    st.subheader("📊 シンプルランキング")
    sorted_simple = sorted(simple_scores.items(), key=lambda x: x[1], reverse=True)
    for i, (b, s) in enumerate(sorted_simple, 1):
        show_rank_card(i, b, simple_percent[b])

# ===============================
# 詳細版
# ===============================
with tab2:
    st.subheader("詳細数値入力")
    detail_data = {}
    for b in boats:
        st.write(f"**{b}号艇**")
        c = st.columns(4)
        m = c[0].number_input("モーター評", 0.0, 10.0, 5.0, 0.1, key=f"dm{b}")
        l = c[1].number_input("当地勝率", 0.0, 10.0, 5.0, 0.1, key=f"dl{b}")
        s = c[2].number_input("平均ST", 0.05, 0.30, 0.18, 0.01, key=f"ds{b}")
        e = c[3].number_input("展示タイム", 6.0, 8.0, 6.90, 0.01, key=f"de{b}")
        detail_data[b] = {"motor": m, "local": l, "start": s, "expo": e}

    st.markdown("#### 重み設定")
    w = st.columns(4)
    wm = w[0].slider("モーター重視", 0, 5, 2)
    wl = w[1].slider("当地重視", 0, 5, 2)
    ws = w[2].slider("ST重視", 0, 5, 2)
    we = w[3].slider("展示重視", 0, 5, 2)

    # 詳細スコア計算（STと展示は低い方が良いため逆数を取る）
    detail_scores = {b: (detail_data[b]["motor"]*wm + detail_data[b]["local"]*wl + (1/detail_data[b]["start"])*ws + (1/detail_data[b]["expo"])*we) for b in boats}
    total_d = sum(detail_scores.values())
    
    st.markdown("---")
    st.subheader("🏆 詳細分析ランキング")
    sorted_detail = sorted(detail_scores.items(), key=lambda x: x[1], reverse=True)
    for i, (b, s) in enumerate(sorted_detail, 1):
        pct = (s / total_d * 100) if total_d > 0 else 0
        show_rank_card(i, b, pct, detail=detail_data[b])

# tab3, tab4 は前回のコードと同様に機能します
