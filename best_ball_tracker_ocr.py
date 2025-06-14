import streamlit as st
from PIL import Image
import pytesseract
import io
from player_db import player_db

st.set_page_config(page_title="Best Ball Tracker OCR")

st.title("🏈 Best Ball Draft Tracker with OCR")
st.write("Upload a draft screenshot to auto-extract player names.")

uploaded_file = st.file_uploader("📸 Upload Screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Screenshot", use_column_width=True)

    with st.spinner("Running OCR..."):
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        text = pytesseract.image_to_string(Image.open(image_bytes))

    st.subheader("📝 Extracted Text")
    st.text(text)

    lines = text.splitlines()
    matched = []
    unmatched = []

    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        found = False
        for short, info in player_db.items():
            if cleaned.lower() in info["full"].lower() or info["full"].lower() in cleaned.lower():
                matched.append(f"{info['full']} ({info['team']} - {info['pos']})")
                found = True
                break
        if not found:
            unmatched.append(cleaned)

    if matched:
        st.subheader("✅ Matched Players")
        for player in matched:
            st.markdown(f"- {player}")
    else:
        st.warning("No players matched.")

    if unmatched:
        st.subheader("❓ Unmatched Lines")
        st.text("\n".join(unmatched))
