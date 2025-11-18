import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
import random
from io import BytesIO

# -----------------------
# Page config
# -----------------------
st.set_page_config(page_title="Generative Poster 2.0", layout="centered")
st.title("🎨 Generative Poster 2.0")
st.write("Interactive generative poster studio — tweak parameters, preview, and download high-resolution PNGs.")

# -----------------------
# Utility: palettes
# -----------------------
PALETTES = {
    "Pastel Minimal": [(255,179,186),(255,223,186),(255,255,186),(186,255,201),(186,225,255)],
    "Vivid": [(255,153,153),(255,204,153),(255,255,153),(153,255,204),(153,204,255)],
    "Noisetouch": [(230,180,180),(230,210,180),(230,230,180),(180,230,210),(180,210,230)],
    "Monochrome": [(50,50,60),(80,80,100),(120,120,140),(160,160,180),(200,200,220)],
    "Neon": [(255,0,102),(0,204,255),(255,204,0),(153,0,255),(0,255,153)]
}

def norm_color(rgb, alpha=1.0):
    r,g,b = rgb
    return (r/255, g/255, b/255, alpha)

# -----------------------
# Element generators
# -----------------------
def draw_irregular_blob(ax, cx, cy, radius, color, points=120, max_offset=0.12, z=1, alpha=0.6):
    angles = np.linspace(0, 2*np.pi, points, endpoint=False)
    xs, ys = [], []
    for a in angles:
        off = random.uniform(-max_offset, max_offset) * radius
        r = radius + off
        xs.append(cx + r * np.cos(a))
        ys.append(cy + r * np.sin(a))
    poly = Polygon(np.column_stack([xs, ys]), closed=True, color=color, zorder=z, ec=None)
    ax.add_patch(poly)

def draw_spiky(ax, cx, cy, radius, spikes=24, irregularity=0.6, color=(0,0,0,0.7), z=1, alpha=0.7):
    angles = np.linspace(0, 2*np.pi, spikes, endpoint=False)
    xs, ys = [], []
    for a in angles:
        r = radius * (1 + np.random.uniform(-irregularity, irregularity))
        xs.append(cx + r * np.cos(a))
        ys.append(cy + r * np.sin(a))
    poly = Polygon(np.column_stack([xs, ys]), closed=True, color=color, zorder=z)
    ax.add_patch(poly)

def draw_gradient_background(ax, width, height, c1, c2):
    # simple vertical gradient via imshow
    grad = np.linspace(0,1,256).reshape(256,1)
    img = np.zeros((256, 1, 4))
    for i in range(3):
        img[:,0,i] = (1-grad) * c1[i] + grad * c2[i]
    img[:,0,3] = 1.0
    ax.imshow(np.repeat(img, 4*width, axis=1), extent=[0,width,0,height], origin='lower', zorder=0)

# -----------------------
# Poster generator
# -----------------------
def generate_poster(width=800, height=1200, n_layers=25, style="Pastel Minimal", seed=None,
                    mode="Blobs", gradient=True, noise=False, shadow=True):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    # Matplotlib figure sized in inches (dpi later)
    dpi = 100
    fig_w, fig_h = width / dpi, height / dpi
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis('off')

    # Background
    palette = PALETTES.get(style, PALETTES["Pastel Minimal"])
    c1 = np.array(palette[0]) / 255.0
    c2 = np.array(palette[-1]) / 255.0
    if gradient:
        draw_gradient_background(ax, width, height, c1, c2)
    else:
        ax.set_facecolor(c1)

    # draw shapes
    for i in range(n_layers):
        cx = random.uniform(0.05*width, 0.95*width)
        cy = random.uniform(0.05*height, 0.95*height)
        base_r = random.uniform(0.06*min(width,height), 0.22*min(width,height))
        color_choice = random.choice(palette)
        alpha = random.uniform(0.35, 0.85)
        color = norm_color(color_choice, alpha=alpha)

        # shadow layer
        if shadow and random.random() < 0.6:
            # draw faint shadow offset
            draw_irregular_blob(ax, cx+base_r*0.08, cy-base_r*0.08, base_r*1.02,
                                norm_color((0,0,0), alpha=0.12), points=120, max_offset=0.18, z=0)

        if mode == "Blobs":
            max_offset = random.uniform(0.03, 0.16)
            draw_irregular_blob(ax, cx, cy, base_r, color, points=140, max_offset=max_offset, z=2, alpha=alpha)
            # some smaller overlay blobs
            if random.random() < 0.35:
                draw_irregular_blob(ax, cx + random.uniform(-base_r, base_r)/2,
                                    cy + random.uniform(-base_r, base_r)/2,
                                    base_r * random.uniform(0.4, 0.8),
                                    norm_color(random.choice(palette), alpha=alpha*0.9),
                                    points=120, max_offset=random.uniform(0.02,0.12), z=3)
        else:  # Spiky
            spikes = random.randint(18, 48)
            draw_spiky(ax, cx, cy, base_r*1.1, spikes=spikes,
                       irregularity=random.uniform(0.2,0.8), color=norm_color(color_choice, alpha=alpha), z=3)

    # optional noise overlay
    if noise:
        arr = np.random.normal(loc=0.0, scale=0.08, size=(int(height/2), int(width/2), 1))
        # tile into RGBA subtle gray
        img = np.concatenate([arr*0 + 0.5, arr*0 + 0.5, arr*0 + 0.5, arr*0 + 0.1], axis=2)
        ax.imshow(img, extent=[0,width,0,height], zorder=10, origin='lower')

    # Title text area (small)
    ax.text(0.03*width, 0.92*height, "Generative Poster 2.0", fontsize=round(width*0.03), fontweight='bold', color='black', zorder=20)
    ax.text(0.03*width, 0.88*height, "Algorithmic Posters • By You", fontsize=round(width*0.015), zorder=20)

    plt.tight_layout(pad=0)
    return fig

# -----------------------
# Streamlit UI controls
# -----------------------
st.sidebar.header("Poster Settings")
preset = st.sidebar.selectbox("Preset / Style",
                              ["Soft Bloom (Pastel Minimal)", "Noisetouch", "Vivid Neon", "Spiky Tension", "Monochrome Calm"])
# map preset to settings
if preset.startswith("Soft"):
    style = "Pastel Minimal"; mode = "Blobs"; gradient = True; noise=False
elif preset.startswith("Noisetouch"):
    style = "Noisetouch"; mode = "Blobs"; gradient=True; noise=True
elif preset.startswith("Vivid"):
    style = "Neon"; mode = "Blobs"; gradient=False; noise=False
elif preset.startswith("Spiky"):
    style = "Vivid"; mode = "Spiky"; gradient=False; noise=False
else:
    style = "Monochrome"; mode = "Blobs"; gradient=True; noise=False

n_layers = st.sidebar.slider("Number of layers", 6, 80, 28)
seed = st.sidebar.number_input("Seed (for reproducible outputs)", min_value=0, value=42)
width_px = st.sidebar.selectbox("Canvas width (px)", [800, 1200, 1600], index=0)
height_px = st.sidebar.selectbox("Canvas height (px)", [1100, 1400, 1800], index=0)
show_shadow = st.sidebar.checkbox("Enable subtle shadows", True)
enable_noise = st.sidebar.checkbox("Enable texture noise", noise)
custom_palette = st.sidebar.selectbox("Palette", list(PALETTES.keys()), index=list(PALETTES.keys()).index(style) if style in PALETTES else 0)

# generate button
if st.button("Generate Poster"):
    fig = generate_poster(width=width_px, height=height_px, n_layers=n_layers,
                          style=custom_palette, seed=seed, mode=mode,
                          gradient=gradient, noise=enable_noise, shadow=show_shadow)
    st.pyplot(fig, bbox_inches='tight')

    # Download high-resolution PNG
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    buf.seek(0)
    st.download_button("Download PNG (high-res)", data=buf, file_name=f"poster_seed{seed}.png", mime="image/png")

    # show small preview thumbnails (3 variations)
    st.subheader("Variations (same settings, different seeds)")
    cols = st.columns(3)
    for i, col in enumerate(cols):
        s = seed + i + 1
        f = generate_poster(width=400, height=600, n_layers=max(8,int(n_layers/2)),
                            style=custom_palette, seed=s, mode=mode, gradient=gradient, noise=enable_noise, shadow=show_shadow)
        buf2 = BytesIO()
        f.savefig(buf2, format="png", dpi=150, bbox_inches='tight')
        buf2.seek(0)
        col.image(buf2)

# Quick info & credits
st.markdown("---")
st.markdown("**How to use**: choose a preset or palette, tweak the layer count and canvas size, set a seed to reproduce results, then press **Generate Poster**. Use the download button to get a high-resolution PNG.")
st.caption("Generative Poster 2.0 • Designed for final project • Code by you + ChatGPT")
