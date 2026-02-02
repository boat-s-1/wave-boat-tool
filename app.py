import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Wave艇予想",
    layout="centered"
)

# -------------------------
# 見た目（SNSスクショ用）
# -------------------------
st.markdown("""
<style>
.rank-card {
    border-radius:16px;
    padding:14px;
    margin-bottom:10px;
    text-align:center;
    font-size:22px;
    font-weight:bold;
}
.badge {
    display:inline-block;
    width:34px;
    height:34px;
    line-height:34px;
    border-radius:50%;
    font-size:18px;
    font-weight:bold;
    margin-right:6px;
}
.b1 {background:#ffffff;color:#000;border:1px solid #ccc;}
.b2 {background:#000000;color:#fff;}
.b3 {background:#e60012;color:#fff;}
.b4 {background:#0068b7;color:#fff;}
.b5 {background:#ffd800;color:#000;}
.b6 {background:#00a95f;color:#fff;}
</style>
""", unsafe_allow_html=True)

st.title("🌊 Wave 競艇予想ツール")

boats = [1,2,3,4,5,6]

symbols = ["☆","◎","〇","□","△","×"]
simple_map = {
    "☆":6,
    "◎":5,
    "〇":4,
    "□":3,
    "△":2,
    "×":1
}

# =====================================================
# 重視モード
# =====================================================

st.subheader("簡易評価モード")

mode = st.radio(
    "評価の重視タイプ",
    ["バランス", "モーター重視", "展示重視", "スタート重視"],
    horizontal=True
)

def weight_set(mode):
    if mode == "モーター重視":
        return {"mark":1.5,"motor":2.0,"local":1.0,"start":1.0,"ex":1.0}
    if mode == "展示重視":
        return {"mark":1.5,"motor":1.0,"local":1.0,"start":1.0,"ex":2.0}
    if mode == "スタート重視":
        return {"mark":1.5,"motor":1.0,"local":1.0,"start":2.0,"ex":1.0}
    return {"mark":1.5,"motor":1.0,"local":1.0,"start":1.0,"ex":1.0}

weights = weight_set(mode)

# =====================================================
# 簡易評価入力
# =====================================================

st.subheader("簡易評価入力（スクショ用ランキング用）")

simple_scores = {}

for b in boats:
    with st.expander(f"{b}号艇 簡易入力", expanded=False):

        mark  = st.selectbox("簡易印", symbols, index=3, key=f"s_m_{b}")
        motor = st.selectbox("モーター", symbols, index=3, key=f"s_motor_{b}")
        local = st.selectbox("当地", symbols, index=3, key=f"s_local_{b}")
        start = st.selectbox("スタート", symbols, index=3, key=f"s_start_{b}")
        ex    = st.selectbox("展示", symbols, index=3, key=f"s_ex_{b}")

        score = (
            simple_map[mark]  * weights["mark"]  +
            simple_map[motor] * weights["motor"] +
            simple_map[local] * weights["local"] +
            simple_map[start] * weights["start"] +
            simple_map[ex]    * weights["ex"]
        )

        simple_scores[b] = score


# =====================================================
# 簡易ランキング表示（順位だけ）
# =====================================================

st.subheader("📸 簡易評価ランキング（スクショ用）")

ranked = sorted(simple_scores.items(), key=lambda x: x[1], reverse=True)

def badge_html(rank, boat):
    return f"""
    <div class="rank-card">
        <span class="badge b{boat}">{boat}</span>
        {rank} 位
    </div>
    """

for i,(b,_) in enumerate(ranked, start=1):
    st.markdown(badge_html(i,b), unsafe_allow_html=True)

# =====================================================
# 詳細版
# =====================================================

st.divider()
st.header("🔍 詳細版（数値入力）")

st.caption("※こちらは精密チェック用。スクショ用ではありません。")

detail_cols = [
    "モーター2連対率",
    "当地勝率",
    "平均ST",
    "展示タイム",
    "直近節成績",
    "過去10走平均着"
]

detail_data = {}

for b in boats:
    with st.expander(f"{b}号艇 詳細入力", expanded=False):

        m2 = st.number_input("モーター2連対率(%)",0.0,100.0,50.0,key=f"d_m2_{b}")
        local = st.number_input("当地勝率",0.0,10.0,5.0,key=f"d_l_{b}")
        stt = st.number_input("平均ST",0.00,0.40,0.15,key=f"d_st_{b}")
        ex = st.number_input("展示タイム",6.00,7.50,6.80,key=f"d_ex_{b}")
        recent = st.slider("直近節成績評価",1,6,3,key=f"d_r_{b}")
        past = st.slider("過去10走平均着",1,6,3,key=f"d_p_{b}")

        detail_data[b] = {
            "motor":m2,
            "local":local,
            "st":stt,
            "ex":ex,
            "recent":recent,
            "past":past
        }

# -------------------------
# 詳細評価モード
# -------------------------

st.subheader("詳細評価モード")

detail_mode = st.radio(
    "詳細評価基準",
    ["バランス","過去10走基準","直近節重視","展示タイム重視"],
    horizontal=True
)

def detail_score(v,mode):

    base = (
        v["motor"]*0.05 +
        v["local"]*0.5 +
        (0.3 - v["st"])*10 +
        (7.2 - v["ex"])*10 +
        (6 - v["recent"]) +
        (6 - v["past"])
    )

    if mode == "過去10走基準":
        base += (6 - v["past"]) * 2

    if mode == "直近節重視":
        base += (6 - v["recent"]) * 2

    if mode == "展示タイム重視":
        base += (7.2 - v["ex"]) * 20

    return base

detail_scores = {}

for b in boats:
    detail_scores[b] = detail_score(detail_data[b], detail_mode)

detail_rank = sorted(detail_scores.items(), key=lambda x:x[1], reverse=True)

st.subheader("詳細評価ランキング")

for i,(b,s) in enumerate(detail_rank, start=1):
    st.write(f"{i}位：{b}号艇")

# =====================================================
# スクショ用メモ
# =====================================================

st.divider()
st.caption("📌 上の『簡易評価ランキング』部分だけをスクショしてX投稿用に使ってください。")
