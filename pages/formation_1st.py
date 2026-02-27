import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw
import base64
import json
import os

st.set_page_config(layout="wide")

IMAGE_PATH = "mark_sheet_base.png"
OUT_PATH = "ticket.png"


# ----------------------
# 座標
# ----------------------

areas_1st = {
    "1st_1": {"x": 234, "y": 355, "r": 9},
    "1st_2": {"x": 270, "y": 355, "r": 9},
    "1st_3": {"x": 308, "y": 355, "r": 9},
    "1st_4": {"x": 234, "y": 410, "r": 9},
    "1st_5": {"x": 270, "y": 410, "r": 9},
    "1st_6": {"x": 308, "y": 410, "r": 9},
}

areas_2nd = {
    "2nd_1": {"x": 338, "y": 355, "r": 9},
    "2nd_2": {"x": 375, "y": 355, "r": 9},
    "2nd_3": {"x": 410, "y": 355, "r": 9},
    "2nd_4": {"x": 338, "y": 410, "r": 9},
    "2nd_5": {"x": 375, "y": 410, "r": 9},
    "2nd_6": {"x": 410, "y": 410, "r": 9},
}

areas_3rd = {
    "3rd_1": {"x": 444, "y": 355, "r": 9},
    "3rd_2": {"x": 480, "y": 355, "r": 9},
    "3rd_3": {"x": 513, "y": 355, "r": 9},
    "3rd_4": {"x": 444, "y": 410, "r": 9},
    "3rd_5": {"x": 480, "y": 410, "r": 9},
    "3rd_6": {"x": 513, "y": 410, "r": 9},
}


# ----------------------
# セッション初期化（超重要）
# ----------------------

for k in ["selected_1st", "selected_2nd", "selected_3rd"]:
    if k not in st.session_state or not isinstance(st.session_state.get(k), list):
        st.session_state[k] = []


# ----------------------
# 画像 base64
# ----------------------

with open(IMAGE_PATH, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()


# ----------------------
# マークUI
# ----------------------

def mark_ui(title, areas, state_key, height=800):

    # DeltaGenerator混入対策
    if not isinstance(st.session_state.get(state_key), list):
        st.session_state[state_key] = []

    areas_json = json.dumps(areas)
    selected_json = json.dumps(st.session_state[state_key])

    html = f"""
    <html>
    <head>
    <style>
    #container {{
      position: relative;
      display: inline-block;
    }}

    .area {{
      position: absolute;
      border-radius: 50%;
      cursor: pointer;
      background: transparent;
      border: 2px solid transparent;
      box-sizing: border-box;
    }}

    .area.selected {{
      border: 3px solid red;
    }}
    </style>
    </head>
    <body>

    <div id="container">
      <img id="img" src="data:image/png;base64,{b64}">
    </div>

    <script>
    const areas = {areas_json};
    let selected = new Set({selected_json});

    const container = document.getElementById("container");
    const img = document.getElementById("img");

    img.onload = () => {{
      for (const [key, a] of Object.entries(areas)) {{
        const d = document.createElement("div");
        d.className = "area";

        d.style.left = (a.x - a.r) + "px";
        d.style.top  = (a.y - a.r) + "px";
        d.style.width  = (a.r * 2) + "px";
        d.style.height = (a.r * 2) + "px";

        if (selected.has(key)) {{
          d.classList.add("selected");
        }}

        d.onclick = () => {{
          if (selected.has(key)) {{
            selected.delete(key);
            d.classList.remove("selected");
          }} else {{
            selected.add(key);
            d.classList.add("selected");
          }}

          window.parent.postMessage({{
            isStreamlitMessage: true,
            type: "streamlit:setComponentValue",
            value: Array.from(selected)
          }}, "*");
        }};

        container.appendChild(d);
      }}
    }}
    </script>
    </body>
    </html>
    """

    st.subheader(title)
    clicked = components.html(html, height=height)

    if isinstance(clicked, list):
        st.session_state[state_key] = clicked

    st.write("選択中：", st.session_state[state_key])


# ----------------------
# 画面
# ----------------------

tab1, tab2, tab3 = st.tabs(["1着", "2着", "3着"])

with tab1:
    mark_ui("1着選択", areas_1st, "selected_1st")

with tab2:
    mark_ui("2着選択", areas_2nd, "selected_2nd")

with tab3:
    mark_ui("3着選択", areas_3rd, "selected_3rd")


# ----------------------
# 舟券画像生成
# ----------------------

if st.button("舟券画像を作成"):

    img = Image.open(IMAGE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    for areas, keys in [
        (areas_1st, st.session_state["selected_1st"]),
        (areas_2nd, st.session_state["selected_2nd"]),
        (areas_3rd, st.session_state["selected_3rd"]),
    ]:
        for k in keys:
            if k not in areas:
                continue

            a = areas[k]
            x, y, r = a["x"], a["y"], a["r"]
            draw.ellipse((x-r, y-r, x+r, y+r), fill="black")

    img.save(OUT_PATH)
    st.success("生成しました")

if os.path.exists(OUT_PATH):
    st.image(OUT_PATH)
