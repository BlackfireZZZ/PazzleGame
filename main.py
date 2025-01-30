import pygame
import os
import random
import split_images  # Импортируем модуль разбиения изображения
from config import Settings

WIDTH, HEIGHT = Settings.WIDTH, Settings.HEIGHT
GRID_SIZE = Settings.GRID_SIZE  # Размер сетки паззла
IMAGE_DIR = Settings.IMAGE_DIR
BACKGROUND_COLOR = Settings.BACKGROUND_COLOR
PUZZLE_OFFSET = Settings.PUZZLE_OFFSET
SNAP_THRESHOLD = Settings.SNAP_THRESHOLD


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drag and Drop Puzzle")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 50)
win_font = pygame.font.Font(None, 80)


def load_images(directory):
    """Загружает все изображения из IMAGE_DIR"""
    return [os.path.join(directory, f) for f in sorted(os.listdir(directory)) if f.startswith("image_")]


def shuffle_image(image_paths, rows, cols):
    """Размещает изображения случайным образом на экране"""
    pieces = []
    piece_width, piece_height = (WIDTH - PUZZLE_OFFSET) // cols, (HEIGHT - PUZZLE_OFFSET) // rows

    for i, path in enumerate(image_paths):
        image = pygame.image.load(path)
        image = pygame.transform.scale(image, (piece_width, piece_height))
        correct_pos = ((i % cols) * piece_width + PUZZLE_OFFSET // 2, (i // cols) * piece_height + PUZZLE_OFFSET // 2)
        pieces.append({"image": image, "current_pos": (
        random.randint(0, WIDTH - piece_width), random.randint(0, HEIGHT - piece_height)), "correct_pos": correct_pos,
                       "index": i})
    return pieces


# Класс игры
class PuzzleGame:
    def __init__(self, image_paths):
        """Инициализирует игру и задает начальные параметры."""
        self.pieces = shuffle_image(image_paths, GRID_SIZE, GRID_SIZE)
        self.selected_piece = None
        self.offset_x = 0
        self.offset_y = 0
        self.game_won = False

    def draw(self, screen):
        """Отображает все куски паззла на экране и проверяет, если игра выиграна, то отображает сообщение о победе."""
        screen.fill(BACKGROUND_COLOR)
        for piece in self.pieces:
            screen.blit(piece["image"], piece["current_pos"])

        if self.game_won:
            text = win_font.render("ВЫ ПОБЕДИЛИ", True, (255, 255, 255))
            text_bg = pygame.Surface((text.get_width() + 40, text.get_height() + 40))
            text_bg.fill((0, 0, 0))
            text_bg.blit(text, (20, 20))
            screen.blit(text_bg, (WIDTH // 2 - text_bg.get_width() // 2, HEIGHT // 2 - text_bg.get_height() // 2))

        pygame.draw.rect(screen, (200, 0, 0), (WIDTH // 2 - 100, HEIGHT - 70, 200, 50))
        restart_text = font.render("Начать заново", True, (255, 255, 255))
        restart_bg = pygame.Surface((restart_text.get_width() + 20, restart_text.get_height() + 20))
        restart_bg.fill((200, 0, 0))
        restart_bg.blit(restart_text, (10, 10))
        screen.blit(restart_bg, (WIDTH // 2 - restart_bg.get_width() // 2, HEIGHT - 70))

    def select_piece(self, pos):
        """Выбирает кусок изображения, который был кликнут пользователем."""
        for i in reversed(range(len(self.pieces))):  # Проверка сверху вниз
            piece = self.pieces[i]
            rect = pygame.Rect(piece["current_pos"], piece["image"].get_size())
            if rect.collidepoint(pos):
                self.selected_piece = self.pieces.pop(i)  # Убираем из списка
                self.offset_x = pos[0] - self.selected_piece["current_pos"][0]
                self.offset_y = pos[1] - self.selected_piece["current_pos"][1]
                self.pieces.append(self.selected_piece)  # Перемещаем наверх
                break

    def move_piece(self, pos):
        """Перемещает выбранный кусок изображения в соответствии с движением мыши."""
        if self.selected_piece is not None:
            new_x = pos[0] - self.offset_x
            new_y = pos[1] - self.offset_y
            self.selected_piece["current_pos"] = (new_x, new_y)

    def release_piece(self):
        """Отпускает выбранный кусок, проверяя, если он находится близко к правильному месту."""
        if self.selected_piece is not None:
            correct_x, correct_y = self.selected_piece["correct_pos"]
            cur_x, cur_y = self.selected_piece["current_pos"]

            # Если кусок близко к правильному месту, привязываем его
            if abs(cur_x - correct_x) < SNAP_THRESHOLD and abs(cur_y - correct_y) < SNAP_THRESHOLD:
                self.selected_piece["current_pos"] = (correct_x, correct_y)

            self.pieces[-1] = self.selected_piece  # Обновляем верхний элемент
            self.selected_piece = None
            self.check_win()

    def check_win(self):
        """Проверяет, все ли кусочки на своих местах."""
        self.game_won = all(piece["current_pos"] == piece["correct_pos"] for piece in self.pieces)

    def restart_game(self):
        """Перезапускает игру, разделяя новое изображение и обновляя его части."""
        split_images.process_images()
        images = load_images(IMAGE_DIR)
        if len(images) == GRID_SIZE * GRID_SIZE:
            self.__init__(images)


# Запуск игры
def main():
    """Основная функция игры, запускает и управляет игровым процессом."""
    split_images.process_images()  # Выбираем случайное фото и разрезаем его

    images = load_images(IMAGE_DIR)
    if len(images) != GRID_SIZE * GRID_SIZE:
        print(f"Ошибка: необходимо {GRID_SIZE * GRID_SIZE} изображений в '{IMAGE_DIR}', но найдено {len(images)}")
        return

    game = PuzzleGame(images)
    running = True

    while running:
        screen.fill(BACKGROUND_COLOR)
        game.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if WIDTH // 2 - 100 <= event.pos[0] <= WIDTH // 2 + 100 and HEIGHT - 70 <= event.pos[1] <= HEIGHT - 20:
                    game.restart_game()
                else:
                    game.select_piece(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                game.move_piece(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                game.release_piece()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
