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
from random import choice, randint
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
BOARD_BACKGROUND_COLOR = (0, 0, 0)
# BOARD_BACKGROUND_COLOR = (200, 200, 200)
BORDER_COLOR = (0, 0, 0)
# BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
# TODO: Хочу сделать BORDER_COLOR черным.

# Пораметры игры:
SPEED = 5
SNAKE_LENGHT = 5  # На мой взгляд не лишняя, как настройка, 
# задаёт длину по умолчпнию
# FIXME: Исправить или написать ревьюеру.

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()
screen.fill(BOARD_BACKGROUND_COLOR)


class GameObject:
    """Базовый класс игровых объектов"""

    def __init__(self, body_color: Optional[tuple] = None) -> None:
        self.position: tuple = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        # добавить пакет для типизации
        self.body_color = body_color
        self.last = None

    def draw(self) -> None:
        """Отрисовывает игровые объекты на игровом поле"""
        rect = (pg.Rect((self.position), (GRID_SIZE, GRID_SIZE)))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


    # def draw_one_cell(self, screen, position, color=None):
    #     """По координатам отрисовываю ячейку заданного цвета"""
    #     if color is None:
    #         color = self.body_color
        

    #     rect = (pg.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE)))
    #     pg.draw.rect(screen, self.body_color, rect)
    #     pg.draw.rect(screen, BORDER_COLOR, rect, 1)
    #     # TODO: Исправлено, доделать вызов.
    #     pass


class Snake(GameObject):
    """Класс игровых объектов Змейка"""

    def __init__(self, length: int = SNAKE_LENGHT,
                 body_color: tuple = SNAKE_COLOR) -> None:
        super().__init__(body_color)
        # Возможность при создания объекта указать длинну змейки,
        self.length: int = length
        self.positions: list = [self.position]
        self.direction: tuple = RIGHT
        self.next_direction: Optional[tuple[int, int]] = None
        # FIXME: лишнее поле
        # Избавьтесь от поля .next_direction.
        # Вместо этого получайте новое направление через параметр метода.·
        self.last: Optional[tuple] = None  # FIXME: сделать что нибудь с last

    def update_direction(self) -> None:
        """Обновляет направления движения змейки после нажатия на кнопку"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию змейки (координаты каждой секции), добавляя новую
        голову в начало списка positions и удаляя последний элемент, если
        длина змейки не увеличилась
        """
        # self.position = self.get_head_position()
        self.position = self.positions[0]

        x_position = ((self.positions[0][0] + self.direction[0] * GRID_SIZE) %
                      SCREEN_WIDTH)
        y_position = ((self.positions[0][1] + self.direction[1] * GRID_SIZE) %
                      SCREEN_HEIGHT)
        head_position = (x_position + SCREEN_WIDTH if (x_position) < 0
                         else x_position,
                         y_position + SCREEN_HEIGHT if (y_position) < 0
                         else y_position)

        past_length: int = len(self.positions)
        self.positions.insert(0, head_position)
        if self.length <= past_length:
            self.last = self.positions.pop()
        else:
            self.last = None

    # def draw(self, screen) -> None:
    #     """Отрисовываю змейку на игровом поле"""
    #     # TODO: удали перед ревью, если не будешь менять цвета
    #     # for position in self.positions[:-1]:
    #     #     rect = (
    #     #         pg.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
    #     #     )
    #     #     color = (0, randrange(150, 255, 5), 0)
    #     #     pg.draw.rect(screen, color, rect)
    #     #     pg.draw.rect(screen, BORDER_COLOR, rect, 1)


    def get_head_position(self) -> tuple:
        """Возвращает позицию головы змейки - первый элемент в списке
        positions
        """
        return self.positions[0]

    def check_collision(self) -> bool:
        """Проверяет столкновение"""
        if self.get_head_position() in self.positions[3:]:
            self.length = SNAKE_LENGHT
            screen.fill(BOARD_BACKGROUND_COLOR)
            self.reset()
            return True
        return False

    def reset(self) -> None:
        """Cбрасывает змейку в начальное состояние после столкновения с
        собой
        """
        self.positions = [self.position]

        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        screen.fill(BOARD_BACKGROUND_COLOR)


class Apple(GameObject):
    """Класс игровых объектов Яблоко"""

    def __init__(self, body_color: tuple = APPLE_COLOR) -> None:
        super().__init__()
        self.randomize_position()
        self.body_color: tuple = body_color

    def randomize_position(self, eater=None) -> None:
        """Устанавливает случайное положение яблока на игровом поле"""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if eater is None or self.position not in eater.positions:
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
                DOWN: {pg.K_LEFT: LEFT, pg.K_RIGHT: RIGHT}
            }
            if event.key in dict_directions[game_object.direction]:
                game_object.next_direction = (
                    dict_directions[game_object.direction][event.key])


def had_ate(object_eat, object_eater) -> None:
    """Проверяет события поедания объекта"""
    if object_eat.position == object_eater.get_head_position():
        object_eater.length += 1
        object_eater.draw()
        object_eater.move()
        object_eat.randomize_position(object_eater)


def main():
    """Выполняется если the_snake запущен напрямую"""
    snake = Snake()
    apple = Apple()

    while True:
        # Изменение скорости с ростом змейки
        # на 1 за 5 съеденных яблок
        game_speed = SPEED + snake.length // 5
        clock.tick(game_speed)
        # Отслеживаем изменения
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        had_ate(apple, snake)
        if snake.check_collision():
            continue
        # Рисуем объекты
        snake.draw()
        apple.draw()
        print()
        pg.display.update()


if __name__ == '__main__':
    main()
