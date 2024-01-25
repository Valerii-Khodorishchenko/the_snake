"""THE_SNAKE.
Модуль представляет собой реализацию игры The snake.
Предпологается, что этот модуль будет запускаться на прямую.
Основной цикл модуля реализован в функции main().

Классы:
GameObject - родительский для всех игровых объектов.
Snake - дочерний класс реализующий игровой объект змейка.
Apple - дочерний класс реализующий игровой объект яблоко.

Функции:
handle_keys - отслеживает действий пользователя
had_ate - логика поведения объектов при поедании объектом змейка

Для ревьюера:
По мимо основного задания реализован выбрдлины змейки константой
SNAKE_LENGH

Изменение скорости в функции main()

Случайный выбор направления при новом старте в методе reset
класса Snake
"""
from random import randint, randrange
from time import sleep
from typing import Optional


import sys
import pygame as pg

# Инициализация PyGame:
pg.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета
BOARD_BACKGROUND_COLOR = (200, 200, 220)
BORDER_COLOR = (200, 200, 220)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SNAKE_BLOOD_COLOR = (230, 66, 245)

# Пораметры игры:
SPEED = 10

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption("Змейка. Для выхода из игры нажмите ESC.")
clock = pg.time.Clock()
screen.fill(BOARD_BACKGROUND_COLOR)


class GameObject:
    """Базовый класс игровых объектов"""

    def __init__(self, body_color=None) -> None:
        self.position: tuple = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        # добавить пакет для типизации
        self.body_color = body_color
        self.last: Optional[tuple] = None

    def draw(self, color=None) -> None:
        """Отрисовывает игровые объекты на игровом поле"""
        # Отрисовка нового сегмента
        if color is None:
            color = self.body_color
        rect = pg.Rect((self.position), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс игровых объектов Змейка"""

    def __init__(
        self, length: Optional[int] = None, body_color: tuple = SNAKE_COLOR
    ) -> None:
        super().__init__(body_color)
        # Возможность при создания объекта указать длинну змейки,
        self.length: int = 5 if length is None else length
        self.positions: list = [self.position]
        self.direction: tuple = RIGHT

    def update_direction(self, direction) -> None:
        """Обновляет направления движения змейки после нажатия на кнопку"""
        self.direction = direction

    def move(self) -> None:
        """Обновляет позицию змейки (координаты каждой секции), добавляя новую
        голову в начало списка positions и удаляя последний элемент, если
        длина змейки не увеличилась
        """
        x_position = ((self.position[0] + self.direction[0] * GRID_SIZE)
                      % SCREEN_WIDTH)
        y_position = ((self.position[1] + self.direction[1] * GRID_SIZE)
                      % SCREEN_HEIGHT)
        self.position = (
            x_position + SCREEN_WIDTH if (x_position) < 0 else x_position,
            y_position + SCREEN_HEIGHT if (y_position) < 0 else y_position,
        )

        past_length: int = len(self.positions)
        self.positions.insert(0, self.position)
        if self.length <= past_length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, color=None) -> None:
        """Рисует змейку"""
        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

        self.draw_body()

        super().draw(color)

    def draw_body(self) -> None:
        """Дополнительно придаёт телу змейки эффект движения"""
        for position in self.positions[:-1]:
            rect = (
                pg.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
            )
            color = (randrange(0, 55, 5), randrange(150, 255, 5), 0)
            pg.draw.rect(screen, color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def get_head_position(self) -> tuple:
        """Возвращает позицию головы змейки - первый элемент в списке
        positions
        """
        return self.positions[0]

    def draw_damage(self):
        """Рисую клетку, в которой змея получила повреждение"""
        self.draw(SNAKE_BLOOD_COLOR)
        pg.display.update()

    def check_collision(self) -> bool:
        """Проверяет столкновение"""
        if self.get_head_position() in self.positions[3:]:
            self.draw_damage()
            sleep(1)
            self.reset()
            return True
        return False

    def reset(self) -> None:
        """Cбрасывает змейку в начальное состояние после столкновения с
        собой
        """
        self.length = 10
        self.positions = [self.position]
        screen.fill(BOARD_BACKGROUND_COLOR)


class Apple(GameObject):
    """Класс игровых объектов Яблоко"""

    def __init__(self, body_color: tuple = APPLE_COLOR) -> None:
        super().__init__(body_color)
        # Начальная позиция всех объектов, в том числе головы змейки.
        # Передовать объект змейка нет необходимости
        position = self.position
        self.randomize_position(position)

    def randomize_position(self, positions) -> None:
        """Устанавливает случайное положение яблока на игровом поле"""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if isinstance(positions, tuple) and self.position != positions:
                break
            elif (isinstance(positions, list)
                  and self.position is not positions):
                break


def handle_keys(game_object):
    """Функция обработки действий пользователя"""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()  # Равносильно raise SystemExit, но с лишним import sys
        elif event.type == pg.KEYDOWN:
            dict_directions = {
                LEFT: {pg.K_UP: UP, pg.K_DOWN: DOWN},
                RIGHT: {pg.K_UP: UP, pg.K_DOWN: DOWN},
                UP: {pg.K_LEFT: LEFT, pg.K_RIGHT: RIGHT},
                DOWN: {pg.K_LEFT: LEFT, pg.K_RIGHT: RIGHT},
            }
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()

            elif event.key in dict_directions[game_object.direction]:
                direction = dict_directions[game_object.direction][event.key]
                return game_object.update_direction(direction)


def had_ate(object_eat, object_eater) -> None:
    """Проверяет события поедания объекта"""
    if object_eat.position == object_eater.get_head_position():
        object_eater.length += 1
        object_eat.randomize_position(object_eater.positions)


def main():
    """Выполняется если the_snake запущен напрямую"""
    snake = Snake(10)
    apple = Apple()
    points = 0
    max_points = 0

    while True:
        # Изменение скорости с ростом змейки
        # на 1 за 5 съеденных яблок
        game_speed = SPEED + snake.length // 5
        clock.tick(game_speed)

        handle_keys(snake)
        snake.move()
        had_ate(apple, snake)
        if snake.check_collision():
            points = 0
            continue
        snake.draw()
        apple.draw()

        points = snake.length
        max_points = max_points if max_points > points else points
        pg.display.set_caption(
            "Змейка. Для выхода из игры нажмите ESC."
            f"Длина змейки: {points}. Рекорд: {max_points}"
        )
        pg.display.update()


if __name__ == "__main__":
    main()
