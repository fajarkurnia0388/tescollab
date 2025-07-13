import math
import os
import time
import shutil

# Constants for the donut's size and animation
A, B = 0, 0  # Rotation angles for animation
ASPECT_RATIO = 0.5  # Typical terminal character height:width ratio
THETA_SPACING = 0.07  # Angle step for the circle
PHI_SPACING = 0.02  # Angle step for the donut
R1 = 1  # Inner radius of the donut
R2 = 2  # Outer radius of the donut
K2 = 5  # Distance from viewer to donut
K1_BASE = K2 * 3 / (8 * (R1 + R2))  # Base scaling factor for projection

# ASCII characters for shading
shades = ".,-~:;=!*#$@"

while True:
    # Dynamically get terminal size
    term_size = shutil.get_terminal_size()
    term_width, term_height = term_size.columns, term_size.lines

    # Ensure dimensions are even for easy division
    total_WIDTH = term_width if term_width % 2 == 0 else term_width - 1
    total_HEIGHT = term_height if term_height % 2 == 0 else term_height - 1

    if total_WIDTH < 20 or total_HEIGHT < 10: # Minimum size check
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Terminal too small to render donuts.")
        time.sleep(0.1)
        continue

    # Calculate quadrant size
    quadrant_WIDTH = total_WIDTH // 2
    quadrant_HEIGHT = total_HEIGHT // 2

    # Adjust K1 for quadrant size
    K1_quadrant = quadrant_WIDTH * K1_BASE

    # Create output and z-buffer arrays for the entire terminal
    output = [' '] * (total_WIDTH * total_HEIGHT)
    zbuffer = [0.0] * (total_WIDTH * total_HEIGHT)

    # Loop through four quadrants (2x2 grid)
    for qy in range(2):
        for qx in range(2):
            quadrant_x_offset = qx * quadrant_WIDTH
            quadrant_y_offset = qy * quadrant_HEIGHT

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

                    # 3D coordinates after rotation (using global A and B for now)
                    x = circlex * (math.cos(B) * cosphi + math.sin(A) * math.sin(B) * sinphi) - circley * math.cos(A) * math.sin(B)
                    y = circlex * (math.sin(B) * cosphi - math.sin(A) * math.cos(B) * sinphi) + circley * math.cos(A) * math.cos(B)
                    z = K2 + math.cos(A) * circlex * sinphi + circley * math.sin(A)
                    ooz = 1 / z  # "One over z" for perspective

                    # Project 3D coordinates to 2D screen positions, centered within the quadrant
                    xp = int(quadrant_WIDTH / 2 + K1_quadrant * ooz * x)
                    yp = int(quadrant_HEIGHT / 2 - K1_quadrant * ooz * y * ASPECT_RATIO)

                    # Calculate luminance (brightness)
                    L = cosphi * costheta * math.sin(B) - math.cos(A) * costheta * sinphi - math.sin(A) * sintheta + math.cos(B) * (math.cos(A) * sintheta - costheta * math.sin(A) * sinphi)
                    luminance_index = int((L + 1.5) * 5)

                    # Only plot if coordinates are within the current quadrant bounds
                    if 0 <= xp < quadrant_WIDTH and 0 <= yp < quadrant_HEIGHT:
                        # Calculate index in the total output buffer
                        idx = (xp + quadrant_x_offset) + (yp + quadrant_y_offset) * total_WIDTH
                        if ooz > zbuffer[idx]:
                            zbuffer[idx] = ooz
                            output[idx] = shades[max(0, min(len(shades) - 1, luminance_index))]
                    phi += PHI_SPACING
                theta += THETA_SPACING

    # Clear the screen and print the frame
    os.system('cls' if os.name == 'nt' else 'clear')
    for i in range(total_HEIGHT):
        row_start = i * total_WIDTH
        row_end = row_start + total_WIDTH
        print(''.join(output[row_start:row_end]))

    # Update rotation angles for animation
    A += 0.04
    B += 0.02
    time.sleep(0.01)
