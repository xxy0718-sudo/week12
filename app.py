import streamlit as st
from PIL import Image
import random
import requests
from io import BytesIO

# ---------------------------------
# Setup
# ---------------------------------
st.set_page_config(page_title="AI Museum Curator", layout="wide")

st.title("🖼️ AI Museum Curator")
st.write("Select artworks, choose a theme, and let the AI generate an exhibition.")

# ---------------------------------
# Image loading function (fix for Streamlit Cloud)
# ---------------------------------
def load_image_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None

# ---------------------------------
# Artwork Library
# ---------------------------------
ARTWORKS = {
    "Starry Night — Van Gogh":
        "https://upload.wikimedia.org/wikipedia/commons/e/ea/The_Starry_Night.jpg",

    "Water Lilies — Monet":
        "https://upload.wikimedia.org/wikipedia/commons/8/8d/Claude_Monet_-_Water_Lilies_-_Google_Art_Project.jpg",

    "The Scream — Munch":
        "https://upload.wikimedia.org/wikipedia/commons/f/f4/The_Scream.jpg",

    "Girl with a Pearl Earring — Vermeer":
        "https://upload.wikimedia.org/wikipedia/commons/d/d7/Meisje_met_de_parel.jpg",

    "Composition VII — Kandinsky":
        "https://upload.wikimedia.org/wikipedia/commons/0/0a/Kandinsky_Composition_VII.jpg"
}

# ---------------------------------
# Display artworks grid
# ---------------------------------
st.markdown("## 1) Artwork Library")

cols = st.columns(3)
for i, (title, url) in enumerate(ARTWORKS.items()):
    img = load_image_from_url(url)
    with cols[i % 3]:
        if img:
            st.image(img, caption=title, use_column_width=True)
        else:
            st.error(f"Failed to load image: {title}")

# ---------------------------------
# Selection
# ---------------------------------
st.markdown("## 2) Choose Artworks for Curation")
selected = st.multiselect("Select artworks:", list(ARTWORKS.keys()))

uploaded_files = st.file_uploader(
    "Or upload your own artworks:",
    accept_multiple_files=True,
    type=["jpg", "jpeg", "png"]
)

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

        # ---------------------------------
        # Display selected artworks
        # ---------------------------------
        st.write("### Selected Artworks & Curatorial Notes")

        for title in selected:
            img = load_image_from_url(ARTWORKS[title])
            if img:
                st.image(img, caption=title, use_column_width=True)
            else:
                st.error(f"Failed to load: {title}")

            st.write(f"""
            **Curatorial Note for *{title}***  
            This artwork relates to **{theme}** through its visual and emotional qualities.  
            Its color, composition, and symbolic meaning contribute to the thematic narrative.  
            """)

        # ---------------------------------
        # Display uploaded artworks
        # ---------------------------------
        for uploaded in uploaded_files:
            img = Image.open(uploaded)
            st.image(img, caption=uploaded.name, use_column_width=True)

            st.write(f"""
            **Curatorial Note for *{uploaded.name}***  
            This work offers a personal interpretation of the theme **{theme}**, 
            reflecting unique textures, tones, and visual storytelling.  
            """)

        # ---------------------------------
        # Exhibition Layout
        # ---------------------------------
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

