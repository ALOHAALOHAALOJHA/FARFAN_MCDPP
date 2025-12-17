import svgwrite
import os

# --- Configuration ---
ASSETS_DIR = "docs_html/assets"
COLORS = {
    "red": "#C41E3A",
    "blue": "#00D4FF",
    "green": "#39FF14",
    "copper": "#B2642E",
    "bg": "#0A0A0A"
}

# --- Asset Generation Functions ---

def generate_texture_red(filename):
    """Generates an organic, flame-like texture."""
    dwg = svgwrite.Drawing(filename, profile='tiny', size=('100%', '100%'))
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=COLORS["bg"]))
    # Add complex SVG filter for flame/smoke effect
    # This is a simplified example
    for i in range(50):
        dwg.add(dwg.circle(center=(f'{i*2}%', f'{i*2}%'), r=f'{i}%', fill=COLORS["red"], opacity=0.1))
    dwg.save()

def generate_texture_blue(filename):
    """Generates a geometric, grid-based texture."""
    dwg = svgwrite.Drawing(filename, profile='tiny', size=('100%', '100%'))
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=COLORS["bg"]))
    for i in range(0, 101, 5):
        dwg.add(dwg.line(start=(f'{i}%', '0%'), end=(f'{i}%', '100%'), stroke=COLORS["blue"], stroke_width=0.5, opacity=0.2))
        dwg.add(dwg.line(start=('0%', f'{i}%'), end=('100%', f'{i}%'), stroke=COLORS["blue"], stroke_width=0.5, opacity=0.2))
    dwg.save()


def generate_texture_green(filename):
    """Generates a neural, filament-like texture."""
    dwg = svgwrite.Drawing(filename, profile='tiny', size=('100%', '100%'))
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=COLORS["bg"]))
    # Add paths that look like neural filaments
    for i in range(20):
        path_d = f"M {i*5} 0 C {i*5+10} 50, {i*5+20} 50, {i*5+30} 100"
        dwg.add(dwg.path(d=path_d, stroke=COLORS["green"], fill='none', stroke_width=0.5, opacity=0.3))
    dwg.save()

def generate_texture_copper(filename):
    """Generates a metallic, oxidized texture."""
    dwg = svgwrite.Drawing(filename, profile='tiny', size=('100%', '100%'))
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=COLORS["bg"]))
    # Add metallic sheen effect
    for i in range(0, 101, 2):
        dwg.add(dwg.line(start=('0%', f'{i}%'), end=('100%', f'{i+1}%'), stroke=COLORS["copper"], stroke_width=1, opacity=0.1))
    dwg.save()


def generate_hexagon_icon(filename, icon_path_d):
    """Generates a hexagonal icon with a given path."""
    dwg = svgwrite.Drawing(filename, profile='tiny', size=('100', '115.47'))
    # Hexagon shape
    points = [(50, 0), (100, 28.87), (100, 86.6), (50, 115.47), (0, 86.6), (0, 28.87)]
    dwg.add(dwg.polygon(points=points, fill=COLORS["bg"], stroke=COLORS["copper"], stroke_width=2))
    # Icon path
    dwg.add(dwg.path(d=icon_path_d, fill=COLORS["blue"]))
    dwg.save()


# --- Main Execution ---

def main():
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)

    # Generate textures
    generate_texture_red(os.path.join(ASSETS_DIR, "texture_red.svg"))
    generate_texture_blue(os.path.join(ASSETS_DIR, "texture_blue.svg"))
    generate_texture_green(os.path.join(ASSETS_DIR, "texture_green.svg"))
    generate_texture_copper(os.path.join(ASSETS_DIR, "texture_copper.svg"))
    print("Generated 4 background textures.")

    # Generate a sample icon
    # In a real scenario, we'd have a dict of paths for all 30 icons
    sample_icon_path = "M50 30 L70 50 L50 70 L30 50 Z" # A simple diamond shape
    generate_hexagon_icon(os.path.join(ASSETS_DIR, "icon_sample.svg"), sample_icon_path)
    print("Generated 1 sample icon.")

if __name__ == "__main__":
    main()
