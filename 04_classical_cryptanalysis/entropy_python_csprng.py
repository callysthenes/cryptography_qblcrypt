import hashlib
import time
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pynput import mouse, keyboard

mouse_movements = []
keystroke_timings = []

print("Move your mouse randomly for entropy... (5 seconds)")
def on_move(x, y):
    # Record high-res timestamps and coords
    mouse_movements.append((time.time(), x, y))
    if len(mouse_movements) > 200:  # safety break
        return False

mouse_listener = mouse.Listener(on_move=on_move)
mouse_listener.start()
time.sleep(5)
mouse_listener.stop()

print("Now, tap keys randomly for entropy... (5 seconds)")
prev_time = time.time()
def on_press(key):
    global prev_time
    t = time.time()
    keystroke_timings.append(t - prev_time)
    prev_time = t
    if len(keystroke_timings) > 100:  # safety break
        return False

keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()
time.sleep(5)
keyboard_listener.stop()

# Mix entropy into a digest
mouse_bytes = b"".join([bytes(str(e), 'utf-8') for e in mouse_movements])
keyboard_bytes = b"".join([bytes(str(e), 'utf-8') for e in keystroke_timings])
collected_entropy = hashlib.sha256(mouse_bytes + keyboard_bytes).hexdigest()

print("Collected user-based entropy hash:", collected_entropy)

# DataFrame/Visualization
df_mouse = pd.DataFrame(mouse_movements, columns=["Time", "X", "Y"])
df_key = pd.DataFrame({"Interval": keystroke_timings})

# Visualize mouse path
if not df_mouse.empty:
    plt.plot(df_mouse['X'], df_mouse['Y'], marker='o')
    plt.title("Mouse Movement Path (Raw Entropy)")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.show()

# Visualize keystroke intervals
if not df_key.empty:
    sns.histplot(df_key['Interval'], bins=20, kde=True, stat="density")
    plt.title("Keystroke Timing Distribution (Entropy Visualization)")
    plt.xlabel("Inter-keystroke Interval (seconds)")
    plt.ylabel("Density")
    plt.show()
