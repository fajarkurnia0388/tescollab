import math
import os
import time
import shutil

# Constants for the donut's size and animation
A, B = 0, 0  # Rotation angles
# For a 500px x 500px area, estimate character size (10px wide x 20px tall):
# WIDTH = 500 / 10 = 50, HEIGHT = 500 / 20 = 25
# Adjust HEIGHT to match WIDTH for a square buffer, and correct for terminal aspect ratio
WIDTH, HEIGHT = 50, 50  # Square buffer for better roundness
ASPECT_RATIO = 0.5  # Typical terminal character height:width ratio
THETA_SPACING = 0.07  # Angle step for the circle
PHI_SPACING = 0.02  # Angle step for the donut
R1 = 1  # Inner radius of the donut
R2 = 2  # Outer radius of the donut
K2 = 5  # Distance from viewer to donut
K1 = WIDTH * K2 * 3 / (8 * (R1 + R2))  # Scaling factor for projection

# ASCII characters for shading
shades = ".,-~:;=!*#$@"

while True:
    # Create output and z-buffer arrays
    output = [' '] * (WIDTH * HEIGHT)
    zbuffer = [0.0] * (WIDTH * HEIGHT)

    # Dynamically get terminal size for centering
    term_size = shutil.get_terminal_size((WIDTH, HEIGHT))
    term_width, term_height = term_size.columns, term_size.lines
    x_offset = (term_width - WIDTH) // 2
    y_offset = (term_height - HEIGHT) // 2

    # Loop over theta (circle around the cross-section of the torus)
    theta = 0
    while theta < 2 * math.pi:
        costheta = math.cos(theta)
        sintheta = math.sin(theta)
        # Loop over phi (circle around the center of the torus)
        phi = 0
        while phi < 2 * math.pi:
            cosphi = math.cos(phi)
            sinphi = math.sin(phi)

            # 3D coordinates before rotation
            circlex = R2 + R1 * costheta
            circley = R1 * sintheta

            # 3D coordinates after rotation
            x = circlex * (math.cos(B) * cosphi + math.sin(A) * math.sin(B) * sinphi) - circley * math.cos(A) * math.sin(B)
            y = circlex * (math.sin(B) * cosphi - math.sin(A) * math.cos(B) * sinphi) + circley * math.cos(A) * math.cos(B)
            z = K2 + math.cos(A) * circlex * sinphi + circley * math.sin(A)
            ooz = 1 / z  # "One over z" for perspective

            # Project 3D coordinates to 2D screen positions, with aspect ratio correction
            xp = int(WIDTH / 2 + K1 * ooz * x)
            yp = int(HEIGHT / 2 - K1 * ooz * y * ASPECT_RATIO)

            # Calculate luminance (brightness)
            L = cosphi * costheta * math.sin(B) - math.cos(A) * costheta * sinphi - math.sin(A) * sintheta + math.cos(B) * (math.cos(A) * sintheta - costheta * math.sin(A) * sinphi)
            luminance_index = int((L + 1.5) * 5)

            # Only plot if coordinates are on screen
            if 0 <= xp < WIDTH and 0 <= yp < HEIGHT:
                idx = xp + yp * WIDTH
                if ooz > zbuffer[idx]:
                    zbuffer[idx] = ooz
                    output[idx] = shades[max(0, min(len(shades) - 1, luminance_index))]
            phi += PHI_SPACING
        theta += THETA_SPACING

    # Clear the screen and print the frame
    os.system('cls' if os.name == 'nt' else 'clear')
    for i in range(term_height):
        if y_offset <= i < y_offset + HEIGHT:
            row_start = (i - y_offset) * WIDTH
            row_end = row_start + WIDTH
            print(' ' * x_offset + ''.join(output[row_start:row_end]) + ' ' * (term_width - x_offset - WIDTH))
        else:
            print(' ' * term_width)
    # Update rotation angles for animation
    A += 0.04
    B += 0.02
    time.sleep(0.01)
