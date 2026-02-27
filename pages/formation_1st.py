import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw
import base64
import json
import os

st.set_page_config(layout="wide")

IMAGE_PATH = "mark_sheet_base.png"
OUT_PATH = "ticket.png"

# ① あなたが取得した座標
areas_1st = {
    "1st_1": {"x": 234, "y": 355, "r": 9},
    "1st_2": {"x": 270, "y": 355, "r": 9},
    "1st_3": {"x": 308, "y": 355, "r": 9},
    "1st_4": {"x": 234, "y": 410, "r": 9},
    "1st_5": {"x": 270, "y": 410, "r": 9},
    "1st_6": {"x": 308, "y": 410, "r": 9},
}

if "selected_1st" not in st.session_state:
    st.session_state.selected_1st = []

with open(IMAGE_PATH, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

areas_json = json.dumps(areas_1st)
selected_json = json.dumps(st.session_state.selected_1st)

# ② 画像＋透明クリックエリア
html = f"""
<!DOCTYPE html>
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
  box-sizing: border-box;
}}
.area.selected {{
  outline: 3px solid red;
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

      const value = Array.from(selected);
      window.parent.postMessage({{
        isStreamlitMessage: true,
        type: "streamlit:setComponentValue",
        value: value
      }}, "*");
    }};

    container.appendChild(d);
  }}
}}
</script>
</body>
</html>
"""

clicked = components.html(html, height=700)

# ③ クリック結果を受け取る
if clicked is not None:
    st.session_state.selected_1st = clicked

st.write("選択中（1着）：", st.session_state.selected_1st)

# ④ 舟券画像を生成
if st.button("舟券画像を作成"):
    img = Image.open(IMAGE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    for k in st.session_state.selected_1st:
        a = areas_1st[k]
        x, y, r = a["x"], a["y"], a["r"]
        draw.ellipse((x-r, y-r, x+r, y+r), fill="black")

    img.save(OUT_PATH)

    st.success("生成しました")

if os.path.exists(OUT_PATH):
    st.image(OUT_PATH)
