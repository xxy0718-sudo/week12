import streamlit as st
import random

# -------------------------------
# Emotion → Color / Shape Mapping
# -------------------------------
EMOTION_COLOR = {
    "Joy": "#FFE082",
    "Calm": "#B2EBF2",
    "Lonely": "#90CAF9",
    "Stress": "#EF9A9A",
    "Love": "#F48FB1",
    "Fear": "#B39DDB",
}

EMOTION_TEXT = {
    "Joy": "A warm, glowing shape that expands like sunlight.",
    "Calm": "Soft gradients blending like quiet waves.",
    "Lonely": "Blue mist dissolving into empty space.",
    "Stress": "Chaotic overlapping lines with sharp tension.",
    "Love": "Gentle curves pulsing with soft pink light.",
    "Fear": "Dark shapes trembling at the edge of the frame.",
}

# -------------------------------
# Page settings
# -------------------------------
st.set_page_config(page_title="EmoCloud - Emotion Visualization", layout="centered")
st.title("🌥️ EmoCloud: Emotion Visualization")
st.write("Record your emotion and let the AI generate a unique visual representation.")

# -------------------------------
# 1) User Emotion Input
# -------------------------------
st.header("① Choose Your Emotion")

emotion = st.selectbox(
    "Pick an emotion:",
    list(EMOTION_COLOR.keys())
)

user_note = st.text_area(
    "Write a short description (optional):",
    placeholder="Example: I feel tired today but also hopeful for something new..."
)

# -------------------------------
# 2) Generate Visualization
# -------------------------------
if st.button("Generate Emotion Visual 🎨"):
    # Randomized visual elements
    size = random.randint(150, 260)
    opacity = random.uniform(0.5, 0.95)
    border_radius = random.randint(10, 180)

    color = EMOTION_COLOR[emotion]
    text = EMOTION_TEXT[emotion]

    st.subheader("② AI Emotion Visualization")
    st.write(text)

    # Visual block (fake AI image using CSS)
    st.markdown(f"""
    <div style="
        width:{size}px;
        height:{size}px;
        background:{color};
        border-radius:{border_radius}px;
        opacity:{opacity};
        margin:auto;
        margin-top:20px;
        box-shadow:0px 0px 30px rgba(0,0,0,0.2);
    ">
    </div>
    """, unsafe_allow_html=True)

    # Emotion log
    st.subheader("③ Emotion Log")
    if user_note.strip():
        st.write(f"**Your note:** {user_note}")
    else:
        st.write("(No text provided.)")

# -------------------------------
# Footer
# -------------------------------
st.write("---")
st.caption("EmoCloud · Built with Streamlit · Designed by ChatGPT + You 💛")
