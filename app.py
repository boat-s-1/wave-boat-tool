import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
from PIL import Image
import io
import datetime
import requests

st.set_page_config(page_title="競艇予想ツール", layout="centered")

boats = [1,2,3,4,5,6]

boat_colors = {
    1:"#ffffff",2:"#000000",3:"#ff0000",
    4:"#0000ff",5:"#ffff00",6:"#00ff00"
}

mark_score = {"☆":6,"◎":5,"〇":4,"□":3,"△":2,"×":1}

# ===============================
# カード表示
# ===============================
def show_rank_card(rank, boat, percent, detail=None):
    medal = ["🥇","🥈","🥉"]
    icon = medal[rank-1] if rank<=3 else f"{rank}位"

    # 30%以上は金色で本命
    if percent >= 30:
        bg = "linear-gradient(135deg,#fff1b8,#ffd700)"
        shadow = "0 0 18px rgba(255,215,0,0.8)"
        badge = "💮 本命"
    # 20%以上は薄ピンクでおすすめ
    elif percent >= 20:
        bg = "linear-gradient(135deg,#ffe6f2,#ffd1ea)"
        shadow = "0 0 10px rgba(255,105,180,0.5)"
        badge = "✨ おすすめ"
    else:
        bg = "linear-gradient(135deg,#ffffff,#f2f2f2)"
        shadow = "0 4px 10px rgba(0,0,0,0.1)"
        badge = ""

    html = f"""
<div style="
border-radius:18px;
padding:14px 16px;
margin-bottom:12px;
background:{bg};
box-shadow:{shadow};
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
モーター {detail['motor']}｜当地 {detail['local']}｜ST {detail['start']}｜展示 {detail['expo']}
</div>
"""
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


st.title("🚤 競艇予想サポートツール")

# ---------------------------
# レース選択
# ---------------------------
c1,c2,c3 = st.columns(3)
with c1:
    race_date = st.date_input("日付", datetime.date.today())
with c2:
    place = st.selectbox("競艇場", ["蒲郡","常滑","浜名湖","津","大村","住之江","若松","芦屋"])
with c3:
    race_no = st.selectbox("レース", list(range(1,13)))
st.caption(f"{race_date}　{place} {race_no}R")

tab1,tab2,tab3 = st.tabs(["⭐簡易版","📊詳細版","📱SNSドラッグ予想"])

# ===============================
# 簡易版
# ===============================
with tab1:
    st.subheader("簡易評価（☆◎〇□△×）")
    simple = {}
    for b in boats:
        st.markdown(f"### {b}号艇")
        c1,c2,c3,c4 = st.columns(4)
        simple[b] = {}
        with c1:
            simple[b]["motor"] = st.selectbox("モーター", list(mark_score), index=3,key=f"sm{b}")
        with c2:
            simple[b]["local"] = st.selectbox("当地", list(mark_score), index=3,key=f"sl{b}")
        with c3:
            simple[b]["start"] = st.selectbox("スタート", list(mark_score), index=3,key=f"ss{b}")
        with c4:
            simple[b]["expo"] = st.selectbox("展示", list(mark_score), index=3,key=f"se{b}")

    simple_scores = {b:sum(mark_score[v] for v in simple[b].values()) for b in boats}
    total_score = sum(simple_scores.values())
    rank = sorted(simple_scores.items(), key=lambda x:x[1], reverse=True)

    st.subheader("簡易ランキング")
    for i,(b,s) in enumerate(rank,1):
        percent = s/total_score*100 if total_score>0 else 0
        show_rank_card(i,b,percent)

# ===============================
# 詳細版
# ===============================
with tab2:
    st.subheader("詳細入力")
    detail={}
    for b in boats:
        st.markdown(f"### {b}号艇")
        c1,c2,c3,c4=st.columns(4)
        with c1: motor=st.number_input("モーター",0.0,10.0,5.0,0.1,key=f"dm{b}")
        with c2: local=st.number_input("当地勝率",0.0,10.0,5.0,0.1,key=f"dl{b}")
        with c3: start=st.number_input("ST",0.05,0.30,0.18,0.01,key=f"ds{b}")
        with c4: expo=st.number_input("展示",6.0,8.0,6.90,0.01,key=f"de{b}")
        detail[b]={"motor":motor,"local":local,"start":start,"expo":expo}

    st.markdown("### 重み設定")
    w1,w2,w3,w4 = st.columns(4)
    with w1: wm=st.slider("モーター重視",0,5,2)
    with w2: wl=st.slider("当地重視",0,5,2)
    with w3: ws=st.slider("ST重視",0,5,2)
    with w4: we=st.slider("展示重視",0,5,2)

    detail_scores={b:detail[b]["motor"]*wm+detail[b]["local"]*wl+(1/detail[b]["start"])*ws+(1/detail[b]["expo"])*we for b in boats}
    dr=sorted(detail_scores.items(),key=lambda x:x[1],reverse=True)
    max_score=max(detail_scores.values())

    st.subheader("詳細ランキング")
    for i,(b,s) in enumerate(dr,1):
        percent = s/max_score*100
        show_rank_card(i,b,percent,detail=detail[b])

# ===============================
# SNSドラッグ予想
# ===============================
with tab3:
    st.subheader("SNS用ドラッグ予想")
    base_mode=st.radio("初期並び",["簡易版ランキング","詳細版ランキング","自由"],horizontal=True)
    if base_mode=="簡易版ランキング": base=rank
    elif base_mode=="詳細版ランキング": base=dr
    else: base=[(b,0) for b in boats]

    objects=[]
    for i,(b,_) in enumerate(base):
        x=160;y=60+i*60
        objects.append({"type":"circle","left":x,"top":y,"radius":22,"fill":boat_colors[b],"stroke":"black","strokeWidth":2})
        objects.append({"type":"text","left":x-8,"top":y-14,"text":str(b),"fontSize":24,"fontWeight":"bold","stroke":"white","strokeWidth":1.5,"fill":"black"})

    if "init" not in st.session_state:
        st.session_state.init=True
        init_draw={"version":"4.4.0","objects":objects}
    else:
        init_draw=None

    # GitHub の raw URL から画像読み込み
    url = "https://raw.githubusercontent.com/boat-s-1/wave-boat-tool/main/mark.png"
    bg = Image.open(requests.get(url,stream=True).raw)

    canvas = st_canvas(
        drawing_mode="transform",
        background_image=bg,
        initial_drawing=init_draw,
        height=500,width=360,
        update_streamlit=True,
        key="canvas"
    )

    st.subheader("ドラッグ後の順位")
    result=[]
    if canvas.json_data:
        for o in canvas.json_data["objects"]:
            if o["type"]=="text":
                try: result.append((int(o["text"]),o["top"]))
                except: pass

    if result:
        result=sorted(result,key=lambda x:x[1])
        for i,(b,_) in enumerate(result,1):
            st.write(f"{i}位　{b}号艇")

