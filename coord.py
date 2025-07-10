import pyautogui
import time
import json

print("Începem în 5 secunde... Comută pe fereastra jocului acum!")
time.sleep(5)

print("\nSelectează cele 9 celule (stânga sus ➡ dreapta jos)")
coords = {}

for i in range(9):
    input(f"[{i}] Pune mouse-ul pe celula {i} și apasă ENTER...")
    pos = pyautogui.position()
    coords[i] = {'center': {'x': pos.x, 'y': pos.y}}
    print(f"Salvat: {pos}")

# Salvăm în fișier
with open("coords.json", "w") as f:
    json.dump(coords, f, indent=4)

print("\nCoordonatele au fost salvate în 'coords.json'")
