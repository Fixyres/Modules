import cv2
import numpy as np
from mss import mss
from pynput.mouse import Controller, Button
import asyncio
import time
import argparse

mouse = Controller()

def load_image_from_file(file_path="png.png"):
    img = cv2.imread(file_path)
    if img is None:
        print("Не удалось загрузить изображение.")
    return img

def convert_to_sketch(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv_gray_img = 255 - gray_img
    blurred_img = cv2.GaussianBlur(inv_gray_img, (21, 21), sigmaX=0, sigmaY=0)
    sketch = cv2.divide(gray_img, 255 - blurred_img, scale=256)
    return sketch

def find_largest_white_square():
    with mss() as sct:
        screenshot = np.array(sct.grab(sct.monitors[0]))
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        _, binary_screenshot = cv2.threshold(gray_screenshot, 250, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary_screenshot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        largest_square = None
        max_area = 0
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if area > max_area and w >= 50 and h >= 50:
                max_area = area
                largest_square = (x, y, w, h)
        return largest_square

def bresenham(x1, y1, x2, y2):
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

    return points

def draw_with_mouse(sketch, region, step):
    x_offset, y_offset, width, height = region
    sketch_resized = cv2.resize(sketch, (width, height), interpolation=cv2.INTER_CUBIC)

    prev_state = None
    for x in range(0, width - 1, step):
        for y in range(0, height - 1, step):
            pixel_value = sketch_resized[y, x]
            if pixel_value < 50 and prev_state != "down":
                mouse.position = (x + x_offset, y + y_offset)
                mouse.press(Button.left)
                prev_state = "down"
            elif pixel_value >= 50 and prev_state != "up":
                mouse.position = (x + x_offset, y + y_offset)
                mouse.release(Button.left)
                prev_state = "up"
                
            if x + step < width and y + step < height:
                next_pixel_value = sketch_resized[y + step, x + step]
                if pixel_value < 50 and next_pixel_value < 50:
                    line_points = bresenham(x + x_offset, y + y_offset, x + step + x_offset, y + step + y_offset)
                    for px, py in line_points:
                        mouse.position = (px, py)
                        mouse.press(Button.left)
                    mouse.release(Button.left)

    mouse.release(Button.left)

async def main(step):
    img = load_image_from_file("png.png")
    if img is None:
        return
    sketch = convert_to_sketch(img)
    print("Ищу место для рисования...")
    region = find_largest_white_square()
    if region is None:
        print("Плаке плаке 😭")
        return
    print(f"Начинаю рисовать...")

    start_time = time.time()

    draw_with_mouse(sketch, region, step)

    print(f"Нарисовал за {time.time() - start_time:.2f} секунд.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Рисование изображения через мышь.")
    parser.add_argument('step', type=int, help="Шаг в пикселях для рисования.")
    args = parser.parse_args()

    asyncio.run(main(args.step))