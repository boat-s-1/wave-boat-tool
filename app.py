import streamlit as st
import datetime


st.set_page_config(layout="wide")

st.title("🚤 競艇 簡易予想ツール")

boats = [1, 2, 3, 4, 5, 6]

# 評価 → 点数
mark_score = {
    "☆": 6,
    "◎": 5,
    "〇": 4,
    "□": 3,
    "△": 2,
    "×": 1
}


# -------------------------
# ランキングカード表示
# -------------------------
def show_rank_card(rank, boat, percent, is_double_circle=False):

    medal = ["🥇", "🥈", "🥉"]
    icon = medal[rank - 1] if rank <= 3 else f"{rank}位"

    # ◎特別表示
    if is_double_circle:
        bg = "linear-gradient(135deg,#fff1f1,#ffd6d6)"
        border = "2px solid #ff4b4b"
        badge = "<span style='margin-left:8px;color:#ff4b4b;font-weight:bold;'>◎本命</span>"
    else:
        bg = "linear-gradient(135deg,#ffffff,#f2f2f2)"
        border = "1px solid #ddd"
        badge = ""

    html = f"""
    <div style="
        border-radius:16px;
        padding:14px 16px;
        margin-bottom:10px;
        background:{bg};
        border:{border};
        box-shadow:0 4px 10px rgba(0,0,0,0.08);
    ">
        <div style="font-size:20px;font-weight:bold;">
            {icon}　{boat}号艇 {badge}
        </div>

        <div style="margin-top:6px;font-size:15px;color:#333;">
            オススメ度：{percent:.1f} %
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


# ---------------------------
# 共通ヘッダ
# ---------------------------
c1,c2,c3 = st.columns(3)

with c1:
    race_date = st.date_input("日付", datetime.date.today())
with c2:
    place = st.selectbox("競艇場",
        ["蒲郡","常滑","浜名湖","津","大村","住之江","若松","芦屋"])
with c3:
    race_no = st.selectbox("レース", list(range(1,13)))

st.caption(f"{race_date}　{place} {race_no}R")

tab1,tab2,tab3 = st.tabs(["⭐簡易版","📊詳細版","📱SNSドラッグ予想"])


# ===============================
# 簡易版
# ===============================

st.subheader("⭐ 簡易評価（☆◎〇□△×）")

simple = {}

for b in boats:
    st.markdown(f"### {b}号艇")
    c1, c2, c3, c4 = st.columns(4)
    simple[b] = {}

    with c1:
        simple[b]["motor"] = st.selectbox(
            "モーター", list(mark_score), index=3, key=f"sm{b}"
        )
    with c2:
        simple[b]["local"] = st.selectbox(
            "当地", list(mark_score), index=3, key=f"sl{b}"
        )
    with c3:
        simple[b]["start"] = st.selectbox(
            "スタート", list(mark_score), index=3, key=f"ss{b}"
        )
    with c4:
        simple[b]["expo"] = st.selectbox(
            "展示", list(mark_score), index=3, key=f"se{b}"
        )

# スコア計算
simple_scores = {
    b: sum(mark_score[v] for v in simple[b].values())
    for b in boats
}

st.subheader("📊 簡易ランキング")

rank = sorted(simple_scores.items(), key=lambda x: x[1], reverse=True)

total_score = sum(simple_scores.values())

for i, (b, s) in enumerate(rank, 1):

    if total_score == 0:
        percent = 0
    else:
        percent = s / total_score * 100

    # ◎が1つでもあれば特別枠
    is_double = any(v == "◎" for v in simple[b].values())

    show_rank_card(
        i,
        b,
        percent,
        is_double_circle=is_double
    )

    
 

# ===============================
# 詳細版
# ===============================
with tab2:

    st.subheader("詳細入力")
    detail={}

    for b in boats:
        st.markdown(f"### {b}号艇")
        c1,c2,c3,c4=st.columns(4)

        with c1:
            motor=st.number_input("モーター",0.0,10.0,5.0,0.1,key=f"dm{b}")
        with c2:
            local=st.number_input("当地勝率",0.0,10.0,5.0,0.1,key=f"dl{b}")
        with c3:
            start=st.number_input("ST",0.05,0.30,0.18,0.01,key=f"ds{b}")
        with c4:
            expo=st.number_input("展示",6.0,8.0,6.90,0.01,key=f"de{b}")

        detail[b]={"motor":motor,"local":local,"start":start,"expo":expo}

    st.markdown("### 重み設定")
    w1,w2,w3,w4=st.columns(4)
    with w1: wm=st.slider("モーター重視",0,5,2)
    with w2: wl=st.slider("当地重視",0,5,2)
    with w3: ws=st.slider("ST重視",0,5,2)
    with w4: we=st.slider("展示重視",0,5,2)

    detail_scores={}
    for b in boats:
        detail_scores[b]=(
            detail[b]["motor"]*wm+
            detail[b]["local"]*wl+
            (1/detail[b]["start"])*ws+
            (1/detail[b]["expo"])*we
        )

    st.subheader("詳細ランキング")
    dr=sorted(detail_scores.items(),key=lambda x:x[1],reverse=True)

    max_score = max(detail_scores.values())

for i, (b, s) in enumerate(dr, 1):

    percent = s / max_score * 100
    is_double = any(v == "◎" for v in simple[b].values())



    show_rank_card(
        i,
        b,
        percent,
        detail=detail[b],
        is_double_circle=is_double
    )

# ===============================
# ドラッグ予想
# ===============================
with tab3:

    st.subheader("SNS用ドラッグ予想")

    base_mode=st.radio("初期並び",
        ["簡易版ランキング","詳細版ランキング","自由"],horizontal=True)

    if base_mode=="簡易版ランキング":
        base=rank
    elif base_mode=="詳細版ランキング":
        base=dr
    else:
        base=[(b,0) for b in boats]

    objects=[]

    for i,(b,_) in enumerate(base):
        x=160
        y=60+i*60

        objects.append({
            "type":"circle","left":x,"top":y,"radius":22,
            "fill":boat_colors[b],"stroke":"black","strokeWidth":2
        })

        objects.append({
            "type":"text","left":x-8,"top":y-14,"text":str(b),
            "fontSize":24,"fontWeight":"bold",
            "stroke":"white","strokeWidth":1.5,"fill":"black"
        })

    if "init" not in st.session_state:
        st.session_state.init=True
        init_draw={"version":"4.4.0","objects":objects}
    else:
        init_draw=None

    bg=Image.open("mark.png")

    canvas=st_canvas(
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
                try:
                    result.append((int(o["text"]),o["top"]))
                except:
                    pass

    if result:
        result=sorted(result,key=lambda x:x[1])
        for i,(b,_) in enumerate(result,1):
            st.write(f"{i}位　{b}号艇")

        st.markdown("### 🧾 あなたの最終予想")
        marks=["◎","〇","▲","△","×","注"]
        for i,(b,_) in enumerate(result,1):
            st.write(f"{marks[i-1]} {b}号艇" if i<=6 else f"{b}号艇")

    if canvas.image_data is not None:
        img=Image.fromarray(np.uint8(canvas.image_data))
        buf=io.BytesIO()
        img.save(buf,format="PNG")

        st.download_button(
            "📥 予想画像を保存",
            buf.getvalue(),
            file_name="boat_prediction.png",
            mime="image/png"
        )





