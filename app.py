import streamlit as st
from PIL import Image
import random
import os

# ---------------------------------
# Setup
# ---------------------------------
st.set_page_config(page_title="AI Museum Curator", layout="wide")

st.title("🖼️ AI Museum Curator")
st.write("Select artworks, choose a theme, and let the AI generate an exhibition.")

st.markdown("## 1) Artwork Library")

# ---------------------------------
# Load sample images
# (You can replace these with your own files)
# ---------------------------------
ARTWORKS = {
    "Starry Night — Van Gogh": "https://upload.wikimedia.org/wikipedia/commons/e/ea/The_Starry_Night.jpg",
    "Water Lilies — Monet": "https://upload.wikimedia.org/wikipedia/commons/8/8d/Claude_Monet_-_Water_Lilies_-_Google_Art_Project.jpg",
    "The Scream — Munch": "https://upload.wikimedia.org/wikipedia/commons/f/f4/The_Scream.jpg",
    "Girl with a Pearl Earring — Vermeer": "https://upload.wikimedia.org/wikipedia/commons/d/d7/Meisje_met_de_parel.jpg",
    "Composition VII — Kandinsky": "https://upload.wikimedia.org/wikipedia/commons/0/0a/Kandinsky_Composition_VII.jpg"
}

# Display artworks as a grid
cols = st.columns(3)
for i, (title, url) in enumerate(ARTWORKS.items()):
    with cols[i % 3]:
        st.image(url, caption=title, use_column_width=True)

# ---------------------------------
# Selection
# ---------------------------------
st.markdown("## 2) Choose Artworks for Curation")
selected = st.multiselect("Select artworks:", list(ARTWORKS.keys()))

uploaded_files = st.file_uploader("Or upload your own artworks:", accept_multiple_files=True, type=["jpg","jpeg","png"])

# ---------------------------------
# Themes
# ---------------------------------
st.markdown("## 3) Curatorial Theme")
theme = st.selectbox(
    "Choose a theme:",
    [
        "Identity & Portraiture",
        "Nature & Emotion",
        "Light, Space & Movement",
        "Modernity vs. Tradition",
        "Chaos & Order",
        "Dream, Memory & Imagination"
    ]
)

# ---------------------------------
# Generate Exhibition
# ---------------------------------
if st.button("Generate Exhibition"):
    if not selected and not uploaded_files:
        st.error("Please select or upload artworks.")
    else:
        st.markdown("## 🏛️ Your Exhibition")
        st.subheader(f"Theme: **{theme}**")

        st.write("### Selected Artworks & Curatorial Notes")

        # Display selected artworks
        for title in selected:
            st.image(ARTWORKS[title], caption=title, use_column_width=True)

            # Generate AI-style curatorial text
            st.write(f"""
            **Curatorial Note for *{title}***  
            This artwork connects to **{theme}** through its exploration of visual language, 
            symbolic meaning, and emotional resonance.  
            Its colors, composition, and historical context contribute to a deeper understanding 
            of how artists express ideas within this theme.  
            """)

        # Display uploaded artworks
        for uploaded in uploaded_files:
            img = Image.open(uploaded)
            st.image(img, caption=uploaded.name, use_column_width=True)

            st.write(f"""
            **Curatorial Note for *{uploaded.name}***  
            This piece reflects the exhibition theme **{theme}**, revealing layers of 
            interpretation through texture, tone, and subject matter.  
            Its visual qualities allow viewers to experience the theme from a personal and 
            contemporary perspective.  
            """)

        # Exhibition layout
        st.write("### Exhibition Layout (Auto-generated)")

        room_count = random.randint(2, 4)
        st.write(f"🗺️ **Gallery Layout — {room_count} Rooms**")

        for i in range(room_count):
            st.write(f"""
            **Room {i+1}: {theme} — Variation {i+1}**  
            • Focus: Color, narrative, and spatial experience  
            • Arrangement: Alternating large and small works  
            • Lighting: Soft directional lighting emphasizing texture  
            """)

        st.success("Exhibition generated successfully!")
