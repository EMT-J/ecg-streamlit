import streamlit as st
import fitz
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import io

def get_background_image(pdf_path, page_number=0, zoom=2):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix)
    img_bytes = pix.tobytes("ppm")
    image = Image.open(io.BytesIO(img_bytes))
    return image

def bpm_to_gap(bpm, scale=0.15):
    return (35.8 / bpm) * scale

def generate_p_waves(start=0.05, end=0.95, wave_width=0.01, bpm=60, base_y=0.23, amp=0.005):
    gap = bpm_to_gap(bpm)
    x_points = []
    y_points = []
    p_ranges = []

    x = start
    while x + wave_width <= end:
        wave_x = np.linspace(x, x + wave_width, 40)
        wave_y = base_y + amp * np.sin(np.linspace(0, np.pi, 40))

        x_points.extend(wave_x)
        y_points.extend(wave_y)
        p_ranges.append((x, x + wave_width))
        x += gap

    return x_points, y_points, p_ranges

def draw_baseline(ax, base_y, exclude_ranges, x_start=0.05, x_end=0.95):
    segments = []
    current_x = x_start

    for ex_start, ex_end in exclude_ranges:
        if current_x < ex_start:
            segments.append((current_x, ex_start))
        current_x = ex_end
    if current_x < x_end:
        segments.append((current_x, x_end))

    for seg_start, seg_end in segments:
        ax.plot([seg_start, seg_end], [base_y, base_y], color='black', linewidth=1)

def render_ecg_plot(pdf_path, bpm):
    bg_image = get_background_image(pdf_path)
    width, height = bg_image.size

    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    ax.imshow(bg_image, extent=[0, 1, 0, 1])

    base_y = 0.23
    x, y, p_ranges = generate_p_waves(base_y=base_y, bpm=bpm)
    draw_baseline(ax, base_y, exclude_ranges=p_ranges)
    ax.plot(x, y, color='black', linewidth=1)

    ax.text(0.25, 0.915, f"{bpm} bpm", fontsize=9, color='black', transform=ax.transAxes)
    ax.axis('off')
    plt.tight_layout()

    return fig

# Streamlit UI
st.title("ECG Generator")
bpm = st.slider("심박수 (BPM)", min_value=30, max_value=180, value=60, step=1)

fig = render_ecg_plot("완전무지 파일.pdf", bpm)
st.pyplot(fig)