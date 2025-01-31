import os
import shutil
import random

from PIL import Image
from config import Settings

# Настройки
SOURCE_DIR = Settings.SOURCE_DIR
OUTPUT_DIR = Settings.IMAGE_DIR
GRID_SIZE = Settings.GRID_SIZE


def clear_output_directory():
    """Очищает папку с нарезанными кусочками."""
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)


def split_image(image_path, grid_size):
    """Разбивает изображение на кусочки и сохраняет их в OUTPUT_DIR."""
    img = Image.open(image_path)
    width, height = img.size
    piece_width = width // grid_size
    piece_height = height // grid_size

    count = 1
    for row in range(grid_size):
        for col in range(grid_size):
            left = col * piece_width
            top = row * piece_height
            right = left + piece_width
            bottom = top + piece_height

            piece = img.crop((left, top, right, bottom))
            piece.save(os.path.join(OUTPUT_DIR, f"image_{count}.png"))
            count += 1


def process_images():
    """Обрабатывает случайное изображение из SOURCE_DIR."""
    clear_output_directory()
    images = [f for f in os.listdir(SOURCE_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]

    if not images:
        print("Ошибка: в 'source_images' нет изображений")
        return

    # Выбираем случайное изображение
    image_path = os.path.join(SOURCE_DIR, random.choice(images))
    split_image(image_path, GRID_SIZE)
    print(f"Изображение {image_path} успешно разбито на {GRID_SIZE * GRID_SIZE} частей.")


if __name__ == "__main__":
    process_images()
