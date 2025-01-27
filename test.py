import cv2

for i in range(1, 101):
    img = cv2.imread(f'Data/Sprites/BeltRight/BeltRight_{i}.png', cv2.IMREAD_UNCHANGED)
    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    cv2.imwrite(f'Data/Sprites/BeltRight/BeltRight_{i}.png', img)