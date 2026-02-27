import streamlit as st
import base64
from pathlib import Path
import streamlit.components.v1 as components


st.set_page_config(layout="wide")

# -----------------------
# 画像を読み込み（自分の画像パスに変更）
# -----------------------
image_path = "sample.png"   # ←あなたの舟券画像

img_bytes = Path(image_path).read_bytes()
img_base64 = base64.b64encode(img_bytes).decode()


# -----------------------
# あなたが送ってくれた座標
# -----------------------
areas = {
    "1st_1": {"x": 234, "y": 355, "r": 12},
    "1st_2": {"x": 270, "y": 355, "r": 12},
    "1st_3": {"x": 308, "y": 355, "r": 12},
    "1st_4": {"x": 234, "y": 410, "r": 12},
    "1st_5": {"x": 270, "y": 410, "r": 12},
    "1st_6": {"x": 308, "y": 410, "r": 12},
}


html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{
  margin: 0;
  padding: 0;
}}

#container {{
  position: relative;
  display: inline-block;
}}

#img {{
  display: block;
  max-width: none;   /* ★ 勝手に縮まない */
}}

.area {{
  position: absolute;
  border: 2px solid rgba(0,0,255,0.5);
  border-radius: 50%;
  cursor: pointer;
  box-sizing: border-box;
}}

.area.selected {{
  background: rgba(255,0,0,0.35);
  border-color: red;
}}
</style>
</head>
<body>

<div id="container">
  <img id="img" src="data:image/png;base64,{img_base64}">
</div>

<script>
const areas = {areas};
const selected = new Set();

const container = document.getElementById("container");
const img = document.getElementById("img");


img.onload = () => {{

  // -----------------------
  // ★ 超重要：元画像サイズで固定
  // -----------------------
  img.style.width  = img.naturalWidth  + "px";
  img.style.height = img.naturalHeight + "px";

  container.style.width  = img.naturalWidth  + "px";
  container.style.height = img.naturalHeight + "px";

  for (const [key, a] of Object.entries(areas)) {{

    const d = document.createElement("div");
    d.className = "area";

    d.style.left   = (a.x - a.r) + "px";
    d.style.top    = (a.y - a.r) + "px";
    d.style.width  = (a.r * 2) + "px";
    d.style.height = (a.r * 2) + "px";

    d.onclick = () => {{
      if (selected.has(key)) {{
        selected.delete(key);
        d.classList.remove("selected");
      }} else {{
        selected.add(key);
        d.classList.add("selected");
      }}

      window.parent.postMessage({{
        type: "selected",
        value: Array.from(selected)
      }}, "*");
    }};

    container.appendChild(d);
  }}

  // -----------------------
  // ★ iframe の高さを画像に合わせる
  // -----------------------
  window.parent.postMessage({{
    type: "streamlit:setFrameHeight",
    height: img.naturalHeight + 20
  }}, "*");

}};
</script>

</body>
</html>
"""


components.html(
    html,
    height=1000,
    scrolling=True
)
