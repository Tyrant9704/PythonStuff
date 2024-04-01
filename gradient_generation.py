import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# tile size
width = 43
height = 58

# doing some settings
third_color_used = False
save_image = True

gradient_type = "linear" #circle, linear
center = (0.5, 0.8) #X, Y

def is_center_valid(center):
    if center is None:
        return False
    if not isinstance(center, tuple):
        return False
    if len(center) != 2:
        return False
    if not all(isinstance(coord, (int, float)) for coord in center):
        return False
    return True

# gradient create
x = np.linspace(0, 1, width)
y = np.linspace(0, 1, height)

# degrees setup
angle_degrees = 135  # 135 = Y axis, 90 = X axis. I don't want to fix it. Circular must be 45, for some fucking reason
angle_radians = np.radians(angle_degrees)

X, Y = np.meshgrid(x, y)

if gradient_type == 'linear':
    X_rotated = X * np.cos(angle_radians) - Y * np.sin(angle_radians)
    Y_rotated = X * np.sin(angle_radians) + Y * np.cos(angle_radians)
elif gradient_type == 'circle':
    if is_center_valid(center):
        X_rotated = X - center[0]
        Y_rotated = Y - center[1]
        R = np.sqrt(X_rotated**2 + Y_rotated**2)
      
        X_rotated = R * np.cos(angle_radians) 
        Y_rotated = R * np.sin(angle_radians) 

    else:
        raise ValueError("Something went wrong. Check your center")
else:
    raise ValueError('Something went wrong. Check your input')

gradient = X_rotated + Y_rotated

# color setup
color_start = [0,0, 0]  # start color (r,g,b)
color_mid = [0, 73, 141] #if third color is False - this will be ignored
color_end = [77, 72, 85]  # end color (r,g,b)

# normalization
color_start_normalized = np.array(color_start) / 255.0
color_mid_normalized = np.array(color_mid) / 255.0
color_end_normalized = np.array(color_end) / 255.0

gradient_min = np.min(gradient)
gradient_max = np.max(gradient)
gradient_scaled = (gradient - gradient_min) / (gradient_max - gradient_min)

# setting up gradient colors and map
if third_color_used == False:
    gradient_colors = np.array([color_start_normalized, color_end_normalized])
else:
    gradient_colors = np.array([color_start_normalized, color_mid_normalized, color_end_normalized])

custom_cmap = LinearSegmentedColormap.from_list("custom", gradient_colors)

# save the shit out

fig, ax = plt.subplots(figsize=(6, 6))  # Ustawienie wielkości rysunku
ax.imshow(gradient, cmap=custom_cmap, vmin=np.min(gradient), vmax=np.max(gradient))
ax.axis('off')  # Wyłączenie osi
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
if save_image == True:
    plt.savefig('black_keyboard_button.png', dpi=300, bbox_inches='tight', pad_inches=0)  # Saving
    print('saved!')
plt.show()


