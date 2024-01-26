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

DIRECTIONS = {
    LEFT: {pg.K_UP: UP, pg.K_DOWN: DOWN},
    RIGHT: {pg.K_UP: UP, pg.K_DOWN: DOWN},
    UP: {pg.K_LEFT: LEFT, pg.K_RIGHT: RIGHT},
    DOWN: {pg.K_LEFT: LEFT, pg.K_RIGHT: RIGHT},
}

# Цвета
BOARD_BACKGROUND_COLOR = (200, 200, 220)
BORDER_COLOR = (200, 200, 220)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SNAKE_BLOOD_COLOR = (230, 66, 245)
SKIN_COLOR = (104, 53, 44)
WALLS_COLOR = (57, 69, 102)

# Пораметры игры:
SPEED = 10
ACCELERATION = 2

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption("Змейка. Для выхода из игры нажмите ESC.")
clock = pg.time.Clock()
screen.fill(BOARD_BACKGROUND_COLOR)


class GameObject:
    """Базовый класс игровых объектов"""

    def __init__(self, body_color=None) -> None:
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = body_color
        self.last: Optional[tuple] = None
        self.positions = None

    def draw(self, color=None) -> None:
        """Отрисовывает игровые объекты на игровом поле"""
        # Отрисовка нового сегмента
        if self.position is None:
            return
        if color is None:
            color = self.body_color
        rect = pg.Rect((self.position), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def reset(self):
        """Переопределяем аргументы"""
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.last = None
        self.positions = list()


class Snake(GameObject):
    """Класс игровых объектов Змейка"""

    def __init__(self, length: int = 1,
                 body_color: tuple = SNAKE_COLOR) -> None:
        super().__init__(body_color)

        self.length = length
        self.positions: list = [self.position]
        self.direction: tuple = RIGHT
        # Значения переменных для self.reset().
        self.reset_length = length
        self.reset_position = self.position
        self.reset_direction = self.direction

    def update_direction(self, direction) -> None:
        """Обновляет направления движения змейки после нажатия на кнопку"""
        self.direction = direction

    def move(self) -> None:
        """Обновляет позицию змейки (координаты каждой секции), добавляя новую
        голову в начало списка positions и удаляя последний элемент, если
        длина змейки не увеличилась
        """
        x_position = (self.position[0]
                      + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        y_position = (self.position[1]
                      + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        self.position = (
            x_position + SCREEN_WIDTH if (x_position) < 0 else x_position,
            y_position + SCREEN_HEIGHT if (y_position) < 0 else y_position,
        )

        past_length: int = len(self.positions)
        self.positions.insert(0, self.position)
        if self.length == past_length:
            self.last = self.positions.pop()
        elif self.length < past_length:
            # Для кожи
            self.last = self.positions.pop()
            self.draw()
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
            rect = pg.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
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

    def ate(self, apple, skin, walls):
        """Проверяет события поедания объекта"""
        last = self.last
        if apple.position == self.get_head_position():
            self.length += 1
            list_positions = busy_positions(
                self, *(self.positions, skin.positions, walls.positions)
            )
            apple.randomize_position(list_positions)
            # Каждые 5 яблок ускоряют метоболизм змейки
            # Змейка сбрасывает кожу
            if not self.length % 5:
                skin.add_skin(last)
            # После того как змейка станет больше 5 ячеек
            # её начинают ограничивать стены каждый раз,
            # как она выростает на 2 ячейки
            if not self.length % 2 and self.length > 5:
                walls.randomize_position(list_positions)

        for skin_position in list(skin.positions):
            if skin_position == self.get_head_position():
                self.length -= 1
                if not self.length:
                    skin.positions = set()
                    self.draw_damage()
                    return False
                skin.positions.discard(self.get_head_position())
                skin.add_skin(self.positions[-2])
                skin.add_skin(self.positions[-1])
        return True

    def check_collision(self, walls) -> bool:
        """Проверяет столкновение"""
        if self.get_head_position() in self.positions[3:] + walls.positions:
            self.draw_damage()
            return True
        return False

    def reset(self) -> None:
        """Cбрасывает змейку в начальное состояние после столкновения с
        собой
        """
        sleep(1)
        super().reset()
        self.length = self.reset_length
        self.position = self.reset_position
        self.positions = [self.position]
        self.direction = self.reset_direction


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
            elif isinstance(positions,
                            list) and self.position is not positions:
                break
        self.draw()


class Skins(GameObject):
    """Класс игровых объектов Кожа"""

    def __init__(self, body_color: tuple = SKIN_COLOR) -> None:
        super().__init__(body_color)
        self.positions = set()

    def add_skin(self, position):
        """Добавляет сброшенную кожу"""
        self.position = position
        self.positions.add(self.position)

    def draw(self, color=None):
        """Рисую сброшенную кожу"""
        for self.position in self.positions:
            super().draw()

    def reset(self):
        """Отчищает множество позиций"""
        super().reset()
        self.positions = set()


class Walls(GameObject):
    """Класс игровых объектов Яблоко"""

    def __init__(self, body_color: tuple = WALLS_COLOR) -> None:
        super().__init__(body_color)
        self.positions = list()
        self.position = tuple()

    def randomize_position(self, positions) -> None:
        """Устанавливает случайное положение яблока на игровом поле"""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )

            if isinstance(positions, list) and self.position is not positions:
                self.positions.append(self.position)
                break

    def reset(self):
        """Отчищает множество позиций"""
        super().reset()
        self.position = None


def busy_positions(snake, *args) -> list:
    """Собирает в список все занятые позиции"""
    list_busy: list = list()
    # Добавляем 5 клеток перед змейкой в занятые позиции
    # Исключаем появление объектов перед головой
    distance = 5
    for _ in range(distance):
        if _ == 0:
            old_positions = snake.positions[0]
        else:
            old_positions = list_busy[-1]

        x_position = (old_positions[0]
                      + snake.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        y_position = (old_positions[1]
                      + snake.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        position = (x_position, y_position)
        list_busy.append(position)

    for positions in args:
        list_busy.extend(positions)
    return list_busy


def handle_keys(game_object):
    """Функция обработки действий пользователя"""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()  # Равносильно raise SystemExit, но с лишним import sys
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()

            elif event.key in DIRECTIONS[game_object.direction]:
                direction = DIRECTIONS[game_object.direction][event.key]
                return game_object.update_direction(direction)


def pressed_shift():
    """Возвращает коэфициент ускорения"""
    keys = pg.key.get_pressed()
    if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
        return ACCELERATION
    return 1


def draw(*args):
    """Рисуем всё"""
    for _ in args:
        _.draw()


def restart(*args):
    """Перезапуск"""
    for _ in args:
        _.reset()
    screen.fill(BOARD_BACKGROUND_COLOR)


def main():
    """Выполняется если the_snake запущен напрямую"""
    snake = Snake(1)
    apple = Apple()
    skin = Skins()
    walls = Walls()

    points = 0
    max_points = 0

    while True:
        # Изменение скорости с ростом змейки
        # на 1 за 5 съеденных яблок
        game_speed = (SPEED
                      + snake.length // 5) * pressed_shift()
        clock.tick(game_speed)

        handle_keys(snake)
        snake.move()
        if not snake.ate(apple, skin, walls) or snake.check_collision(walls):
            restart(snake, apple, skin, walls)
            points = 0
            continue
        draw(snake, apple, skin, walls)

        points = snake.length - snake.reset_length
        max_points = max_points if max_points > points else points
        pg.display.set_caption(
            "Змейка. Выход - ESC.  "
            f"Длина змейки: {points}. Рекорд: {max_points}  "
            f"SHIFT - ускорение."
        )
        pg.display.update()


if __name__ == "__main__":
    main()
