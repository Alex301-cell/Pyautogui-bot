import pyautogui
import time

print("Începem în 5 secunde... Comută pe fereastra jocului acum!")
time.sleep(5)

print("\nSelectează cele 9 celule (stânga sus ➡ dreapta jos)")
coords = []

for i in range(9):
    input(f"[{i}] Pune mouse-ul pe celula {i} și apasă ENTER...")
    pos = pyautogui.position()
    coords.append(pos)
    print(f"Salvat: {pos}")

print("\nCoordonate finale:")
for i, coord in enumerate(coords):
    print(f"cell_{i} = {coord}")

