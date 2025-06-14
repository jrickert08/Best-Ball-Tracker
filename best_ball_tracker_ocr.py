import streamlit as st
from player_db import player_db
import pytesseract
from PIL import Image
import io

st.set_page_config(page_title="🧠 Best Ball Draft Tracker with OCR", layout="wide")

st.title("📸 Upload Screenshot for OCR")
uploaded_file = st.file_uploader("Upload a draft screenshot for OCR", type=["png", "jpg", "jpeg"])

draft_players = []

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    text = pytesseract.image_to_string(image)
    lines = text.splitlines()

    matched_players = []
    unmatched_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        matched = False
        for short_name in player_db:
            if short_name in line:
                matched_players.append((short_name, player_db[short_name]))
                matched = True
                break
        if not matched:
            unmatched_lines.append(line)

    if matched_players:
        st.success("✅ Matched Players")
        for short, data in matched_players:
            st.write(f"{data['full']} ({data['team']} - {data['pos']})")
            draft_players.append(data['full'])
    else:
        st.warning("⚠️ No players matched from OCR. Check image clarity.")

    if unmatched_lines:
        with st.expander("Unmatched Text Lines"):
            st.text("
".join(unmatched_lines))

st.markdown("---")
st.header("📝 Add Draft Manually")
contest = st.text_input("Contest Name (e.g., Best Ball Mania, Puppy, DK $5)")
manual_input = st.text_area("Enter player names (one per line, exactly as listed):")

if st.button("➕ Add Draft"):
    names = manual_input.splitlines()
    st.success(f"Added draft to {contest} with {len(names)} players.")
