# app.py
import streamlit as st
import io
import os
import base64
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

# Optional OpenAI: used only if key provided
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

# -----------------------
# Page config
# -----------------------
st.set_page_config(page_title="Generative Studio", layout="wide")
st.title("🎨 Generative Studio — AI-Assisted Art Creation & Prompt Lab")
st.write("Craft prompts, generate images (OpenAI DALL·E if API key present), iterate, and curate a portfolio.")

# -----------------------
# Sidebar: keys & settings
# -----------------------
st.sidebar.header("Settings & API")
openai_key = st.sidebar.text_input("OpenAI API Key (optional)", type="password",
                                   help="Paste your OpenAI API key here or set OPENAI_API_KEY in Streamlit Secrets for deployment.")
use_openai = False
if openai_key:
    if OPENAI_AVAILABLE:
        openai.api_key = openai_key.strip()
        use_openai = True
    else:
        st.sidebar.error("openai package not installed in environment. Fallback to local generator.")
else:
    # try secrets
    try:
        key_from_secrets = st.secrets["OPENAI_API_KEY"]
        if OPENAI_AVAILABLE:
            openai.api_key = key_from_secrets
            use_openai = True
            st.sidebar.write("Using OpenAI key from Streamlit Secrets.")
        else:
            st.sidebar.info("OpenAI SDK not installed; local fallback will be used.")
    except Exception:
        pass

st.sidebar.markdown("---")
st.sidebar.header("Output & Gallery")
gallery_capacity = st.sidebar.slider("Gallery capacity", 3, 30, 12)
export_zip = st.sidebar.checkbox("Enable export ZIP for downloaded images", True)

# -----------------------
# Prompt builder UI
# -----------------------
st.subheader("1) Prompt Builder")

col_a, col_b, col_c = st.columns([3,2,2])

with col_a:
    subject = st.text_input("Subject / Main motif", "A lone figure under a neon umbrella")
    style = st.selectbox("Style", ["photorealistic", "oil painting", "watercolor", "digital art", "surrealist", "collage"])
    mood = st.selectbox("Mood / Emotion", ["melancholy", "joyful", "mysterious", "calm", "tense"])
    details = st.text_area("Extra details (composition, lighting, camera)", "three-quarter view, cinematic lighting, shallow depth of field")

with col_b:
    color_palette = st.selectbox("Color palette", ["pastel", "neon", "muted", "warm", "cool", "monochrome"])
    composition = st.selectbox("Composition hint", ["close-up portrait", "wide landscape", "centered subject", "rule of thirds"])
    aspect = st.selectbox("Aspect ratio", ["4:5 (portrait)", "1:1 (square)", "16:9 (landscape)"])

with col_c:
    # guidance for prompt engineering
    st.markdown("**Prompt engineering tips**")
    st.markdown("- Add a few concrete style references (e.g., 'in the style of Vermeer' or 'cinematic, 35mm film').")
    st.markdown("- Mention lighting and material properties (e.g., 'soft rim light', 'matte paper texture').")
    st.markdown("- Use adjectives for mood and clarity.")

# assembled prompt preview
base_prompt = f"{subject}, {style}, mood: {mood}, colors: {color_palette}, composition: {composition}, {details}"
st.markdown("**Prompt preview:**")
st.code(base_prompt, language="text")

# seed and attempts
col_seed, col_attempts = st.columns(2)
with col_seed:
    seed = st.number_input("Seed (0 = random)", min_value=0, value=0, step=1)
with col_attempts:
    n_variations = st.slider("Variations to generate", 1, 6, 3)

# -----------------------
# Local procedural generator (fallback)
# -----------------------
def procedural_mock_image(prompt_text, w=1024, h=1024, seed=None, palette="pastel"):
    if seed and seed > 0:
        random.seed(seed)
        np.random.seed(seed)
    else:
        random.seed()
        np.random.seed()

    # generate simple abstract composition using PIL
    img = Image.new("RGBA", (w, h), (255,255,255,255))
    draw = ImageDraw.Draw(img)

    # palette choices
    PALETTES = {
        "pastel": [(255,179,186),(255,223,186),(255,255,186),(186,255,201),(186,225,255)],
        "neon": [(255,0,102),(0,204,255),(255,204,0),(153,0,255),(0,255,153)],
        "muted": [(150,120,120),(120,140,130),(130,120,160),(180,170,160)],
        "warm": [(255,179,102),(255,120,60),(220,80,40),(180,40,20)],
        "cool": [(80,160,200),(50,100,150),(30,60,100),(20,40,70)],
        "monochrome": [(30,30,40),(70,70,90),(110,110,130),(160,160,180)]
    }
    colors = PALETTES.get(palette, PALETTES["pastel"])

    # background gradient
    bg1 = colors[0]
    bg2 = colors[-1]
    for i in range(h):
        t = i / h
        r = int((1-t)*bg1[0] + t*bg2[0])
        g = int((1-t)*bg1[1] + t*bg2[1])
        b = int((1-t)*bg1[2] + t*bg2[2])
        draw.line([(0,i),(w,i)], fill=(r,g,b,255))

    # draw blobs
    n_blobs = random.randint(6,18)
    for i in range(n_blobs):
        rx = random.randint(int(0.05*w), int(0.95*w))
        ry = random.randint(int(0.05*h), int(0.95*h))
        r = random.randint(int(0.06*min(w,h)), int(0.22*min(w,h)))
        color = random.choice(colors)
        alpha = random.randint(120,220)
        # draw many layered ellipses to create soft shapes
        layer = Image.new("RGBA", (w,h), (255,255,255,0))
        ld = ImageDraw.Draw(layer)
        for rr in range(r, int(r*0.2), -int(r*0.1) if r>10 else -1):
            bbox = [rx-rr, ry-rr, rx+rr, ry+rr]
            lc = (color[0], color[1], color[2], int(alpha * (rr/(r+1))))
            ld.ellipse(bbox, fill=lc)
        # blur layer slightly
        layer = layer.filter(ImageFilter.GaussianBlur(radius=random.uniform(6,18)))
        img = Image.alpha_composite(img, layer)

    # add text annotation (the prompt shortened)
    try:
        fnt = ImageFont.truetype("DejaVuSans.ttf", size=28)
    except Exception:
        fnt = ImageFont.load_default()
    text = (prompt_text[:120] + '...') if len(prompt_text) > 120 else prompt_text
    draw = ImageDraw.Draw(img)
    txt_w, txt_h = draw.textsize(text, font=fnt)
    draw.rectangle([(10, h-10-txt_h-10), (10+txt_w+12, h-10)], fill=(255,255,255,200))
    draw.text((16, h-10-txt_h-6), text, fill=(30,30,40,255), font=fnt)

    return img.convert("RGB")

# -----------------------
# Image generation function (OpenAI Image API)
# -----------------------
def generate_with_openai(prompt_text, size="1024x1024", n=1):
    # This function requires openai.api_key to be set and openai package installed.
    try:
        resp = openai.Image.create(prompt=prompt_text, n=n, size=size)
        images = []
        for item in resp['data']:
            b64 = item['b64_json']
            img = Image.open(io.BytesIO(base64.b64decode(b64)))
            images.append(img.convert("RGB"))
        return images
    except Exception as e:
        st.error(f"OpenAI generation error: {e}")
        return []

# -----------------------
# Generate / iterate controls
# -----------------------
st.subheader("2) Generate & Iterate")

generate_col1, generate_col2 = st.columns([1,1])
with generate_col1:
    if st.button("Generate Images"):
        # ensure prompt built
        prompt = base_prompt
        gallery = st.session_state.get("gallery", [])
        new_images = []

        # decide palette param for procedural fallback
        palette_param = color_palette = color_palette if 'color_palette' in locals() else "pastel"
        # generate variations
        for i in range(n_variations):
            this_seed = seed + i if seed and seed>0 else random.randint(1, 2**31-1)
            if use_openai:
                st.info(f"Generating variation {i+1} with OpenAI (seed {this_seed})...")
                imgs = generate_with_openai(prompt, size="1024x1024", n=1)
                if imgs:
                    img = imgs[0]
                else:
                    st.warning("Falling back to local generator for this variation.")
                    img = procedural_mock_image(prompt, w=1024, h=1024, seed=this_seed, palette=palette_param)
            else:
                st.info(f"Generating variation {i+1} locally (seed {this_seed})...")
                img = procedural_mock_image(prompt, w=1024, h=1024, seed=this_seed, palette=palette_param)
            # store image & metadata in gallery
            metadata = {"prompt": prompt, "seed": this_seed, "style": style, "mood": mood, "palette": color_palette}
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            gallery.insert(0, {"image_bytes": img_bytes.getvalue(), "meta": metadata})
            # cap gallery
            if len(gallery) > gallery_capacity:
                gallery = gallery[:gallery_capacity]
            new_images.append(img)
        # save session state
        st.session_state["gallery"] = gallery
        st.success(f"{len(new_images)} images generated and added to gallery.")

with generate_col2:
    if st.button("Clear Gallery"):
        st.session_state["gallery"] = []
        st.success("Gallery cleared.")

# -----------------------
# 3) Gallery & Export
# -----------------------
st.subheader("3) Gallery")
gallery = st.session_state.get("gallery", [])
if not gallery:
    st.info("No images in gallery yet — generate some above.")
else:
    # display gallery with simple controls
    cols = st.columns(3)
    for idx, item in enumerate(gallery):
        col = cols[idx % 3]
        img = Image.open(io.BytesIO(item["image_bytes"]))
        col.image(img, use_column_width=True)
        col.markdown(f"**Seed:** {item['meta']['seed']}")
        col.markdown(f"**Prompt:** {item['meta']['prompt'][:80]}...")
        # download single image
        btn_key = f"dl_{idx}"
        col.download_button(label="Download PNG", data=item["image_bytes"],
                            file_name=f"gen_{item['meta']['seed']}.png", mime="image/png", key=btn_key)

# export zip
if export_zip and gallery:
    import zipfile, tempfile
    if st.button("Export Gallery as ZIP"):
        with tempfile.TemporaryFile() as tmpf:
            with zipfile.ZipFile(tmpf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                for i, itm in enumerate(gallery):
                    zf.writestr(f"image_{i+1}_seed{itm['meta']['seed']}.png", itm["image_bytes"])
            tmpf.seek(0)
            st.download_button("Download ZIP", data=tmpf.read(), file_name="gallery.zip", mime="application/zip")

# -----------------------
# 4) Prompt notebook & advise
# -----------------------
st.subheader("4) Prompt Notebook & Tips")
st.markdown("- Try swapping the style and mood fields to see strong changes in outputs.")
st.markdown("- Use seeds to reproduce favorites. Seed 0 = fully random.")
st.markdown("- Keep prompt length clear: subject → style → mood → colors → composition → reference artists.")
st.markdown("- Example prompt: 'A melancholic neon city street, cinematic lighting, shallow depth of field, in the style of a futuristic noir poster.'")

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.caption("Generative Studio • Designed for creative experimentation. Save seeds and prompts to reproduce your favorite outputs.")
