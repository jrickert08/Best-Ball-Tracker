
import streamlit as st
import pandas as pd
from collections import defaultdict
import requests
from PIL import Image
import io

st.set_page_config(page_title="Best Ball Draft Tracker", layout="wide")
st.title("🏈 Best Ball Tracker - Underdog & DraftKings")

# Storage for all drafts
if "drafts" not in st.session_state:
    st.session_state.drafts = []

# Player metadata
def get_player_db():
    return {
        "C. Williams": {"team": "CHI", "pos": "QB", "bye": 5},
        "K. Walker III": {"team": "SEA", "pos": "RB", "bye": 8},
        "K. Johnson": {"team": "PIT", "pos": "RB", "bye": 5},
        "C. Lamb": {"team": "DAL", "pos": "WR", "bye": 10},
        "R. Rice": {"team": "KC", "pos": "WR", "bye": 10},
        "X. Worthy": {"team": "KC", "pos": "WR", "bye": 10},
        "B. Bowers": {"team": "LV", "pos": "TE", "bye": 8},
        "R. Odunze": {"team": "CHI", "pos": "WR", "bye": 5},
        "D. Prescott": {"team": "DAL", "pos": "QB", "bye": 10},
        "L. Burden III": {"team": "CHI", "pos": "WR", "bye": 5},
        "J. Williams": {"team": "DAL", "pos": "RB", "bye": 10},
        "J. Ferguson": {"team": "DAL", "pos": "TE", "bye": 10},
        "R. Shaheed": {"team": "NO", "pos": "WR", "bye": 11},
        "A. Ekeler": {"team": "WAS", "pos": "RB", "bye": 12},
        "Q. Johnston": {"team": "LAC", "pos": "WR", "bye": 12},
        "J. Noel": {"team": "HOU", "pos": "WR", "bye": 6},
        "W. Shipley": {"team": "PHI", "pos": "RB", "bye": 9},
        "W. Marks": {"team": "HOU", "pos": "RB", "bye": 6},
        "J. Milroe": {"team": "SEA", "pos": "QB", "bye": 8},
        "R. Wilson": {"team": "PIT", "pos": "WR", "bye": 5},
    }

player_db = get_player_db()

# OCR Upload
st.header("📸 Upload Screenshot for OCR")
ocr_image = st.file_uploader("Upload a draft screenshot for OCR", type=["png", "jpg", "jpeg"])
ocr_team = []
if ocr_image:
    st.image(ocr_image, caption="Uploaded Image", use_column_width=True)
    img_bytes = ocr_image.read()
    api_key = "helloworld"  # Replace with your real key for production

    with st.spinner("Extracting text via OCR..."):
        res = requests.post(
            "https://api.ocr.space/parse/image",
            files={"screenshot.jpg": img_bytes},
            data={"apikey": api_key, "language": "eng"}
        )
        result = res.json()
        text = result.get("ParsedResults", [{}])[0].get("ParsedText", "")
        lines = text.splitlines()
        for line in lines:
            for name in player_db:
                if name in line:
                    ocr_team.append({"player": name, **player_db[name]})
                    break

    if ocr_team:
        st.success("Players extracted from image:")
        st.dataframe(pd.DataFrame(ocr_team))
        contest_name = st.text_input("Contest Name for OCR Upload", key="ocr")
        if st.button("Save OCR Draft"):
            st.session_state.drafts.append({"contest": contest_name, "players": ocr_team})
            st.success("OCR draft added!")
    else:
        st.warning("No players matched from OCR. Check image clarity.")

# Manual entry
st.header("📝 Add Draft Manually")
contest_name = st.text_input("Contest Name (e.g., Best Ball Mania, Puppy, DK $5)")
player_names = st.text_area("Enter player names (one per line, exactly as listed):")

if st.button("Save Draft"):
    draft_team = []
    for name in player_names.splitlines():
        if name.strip() in player_db:
            entry = {"player": name.strip(), **player_db[name.strip()]}
            draft_team.append(entry)

    if draft_team:
        st.session_state.drafts.append({"contest": contest_name, "players": draft_team})
        st.success("Draft added!")
    else:
        st.warning("No valid players found. Make sure names match exactly.")

# Filter by contest
st.header("🔍 Filter by Contest")
all_contests = list(set(d["contest"] for d in st.session_state.drafts))
selected_contests = st.multiselect("Show drafts from these contests:", all_contests, default=all_contests)

# Exposure Dashboard
st.header("📊 Exposure Dashboard")
exposure = defaultdict(int)
for draft in st.session_state.drafts:
    if draft["contest"] in selected_contests:
        for player in draft["players"]:
            exposure[player["player"]] += 1

if exposure:
    df = pd.DataFrame([
        {"Player": k, "Team": player_db[k]["team"], "Pos": player_db[k]["pos"], "Drafts": v}
        for k, v in exposure.items()
    ]).sort_values("Drafts", ascending=False)
    st.dataframe(df)
else:
    st.info("No exposure data available. Add drafts or adjust contest filter.")

# Future planned features
st.header("🔮 Planned Features Coming Soon")
st.markdown("""
- 🧠 **Teammate Stack Detection**
- 🔄 **Week 15–17 Opponent Correlation Finder**
- 📈 **ADP vs Draft Value Analyzer**
- 📦 **Export Draft Portfolio to CSV/Excel**
- ☁️ **Cloud Save / Load Option for Portfolios**
- 🔍 **Filter/Sort by Team, Position, Bye Week, Round**
- 🔗 **Integration with schedule & projections APIs**
""")
