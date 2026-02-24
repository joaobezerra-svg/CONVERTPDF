import numpy as np
from PIL import Image, ImageDraw

def draw_hexagon(draw, center, size, outline_color, fill_color, border_width):
    x, y = center
    points = []
    for i in range(6):
        # Rotated to have flat top/bottom instead of pointy top
        angle_deg = 60 * i
        angle_rad = np.pi / 180 * angle_deg
        points.append((x + size * np.cos(angle_rad), y + size * np.sin(angle_rad)))
    
    draw.polygon(points, fill=fill_color)
    draw.polygon(points, outline=outline_color, width=border_width)

def generate_background(width=1920, height=1080):
    image = Image.new('RGB', (width, height), '#05000A')
    draw = ImageDraw.Draw(image)
    
    hex_size = 90
    border_width = 3 # thin bright borders
    
    # Grid math for flat-topped hexagons
    h_dist = hex_size * 1.5
    v_dist = hex_size * np.sqrt(3)
    
    cols = int(width / h_dist) + 2
    rows = int(height / v_dist) + 2
    
    base_fill = (10, 5, 20)
    
    center_x, center_y = width / 2, height / 2

    # Draw Glow behind hexagons
    for r in range(0, width, 10):
         pass # A radial gradient is hard in PIL purely, we will do it via CSS in streamlit
         
    for row in range(rows):
        for col in range(cols):
            x = col * h_dist
            y = row * v_dist
            
            if col % 2 == 1:
                y += v_dist / 2
                
            # Distance from center
            dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            max_dist = np.sqrt(center_x**2 + center_y**2)
            glow_factor = max(0, 1 - (dist / (max_dist * 0.9)))
            
            # The reference has bright purple borders (#A619FF approx)
            glow_r = int(70 + (130 * glow_factor))
            glow_g = int(10 + (25 * glow_factor))
            glow_b = int(120 + (135 * glow_factor))
            
            outline_color = (glow_r, glow_g, glow_b)
            # The inner fill has a very slight purple tint in the center
            fill_r = int(10 + (30 * glow_factor))
            fill_g = int(5 + (10 * glow_factor))
            fill_b = int(20 + (40 * glow_factor))
            fill_color = (fill_r, fill_g, fill_b)
            
            draw_hexagon(draw, (x, y), hex_size - 4, outline_color, fill_color, border_width)

    image.save('background.png')

if __name__ == '__main__':
    generate_background()
