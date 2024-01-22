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
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Пораметры игры:
SPEED = 5
SNAKE_LENGH = 5

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс игровых объектов"""

    def __init__(self) -> None:
        self.position: tuple = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        # добавить пакет для типизации
        self.body_color: Optional[tuple] = None

    def draw(self, surface) -> None:
        """Отрисовывает игровые объекты на игровом поле"""


class Snake(GameObject):
    """Класс игровых объектов Змейка"""

    def __init__(self, length: int = 1,
                 body_color: tuple = SNAKE_COLOR) -> None:
        super().__init__()
        # Возможность при создания объекта указать длинну змейки,
        # По умолчанию length = 1.
        self.new_game_length: int = length
        self.length: int = self.new_game_length
        self.positions: list = [self.position]
        self.direction: tuple = RIGHT
        self.next_direction: Optional[tuple[int, int]] = None
        self.body_color: tuple = body_color
        self.last: Optional[tuple] = None

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
        head_posirion = (self.positions[0][0] + self.direction[0] * GRID_SIZE,
                         self.positions[0][1] + self.direction[1] * GRID_SIZE
                         )
        # Условия конца поля
        if head_posirion[0] >= SCREEN_WIDTH:
            head_posirion = (0, head_posirion[1])
        if head_posirion[0] < 0:
            head_posirion = (SCREEN_WIDTH - GRID_SIZE, head_posirion[1])
        if head_posirion[1] >= SCREEN_HEIGHT:
            head_posirion = (head_posirion[0], 0)
        if head_posirion[1] < 0:
            head_posirion = (head_posirion[0], SCREEN_HEIGHT - GRID_SIZE)
        past_length: int = len(self.positions)
        self.positions.insert(0, head_posirion)
        if self.length <= past_length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, surface) -> None:
        """Отрисовываю змейку на игровом поле"""
        for position in self.positions[:-1]:
            rect = (
                pg.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
            )
            pg.draw.rect(surface, self.body_color, rect)
            pg.draw.rect(surface, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pg.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(surface, self.body_color, head_rect)
        pg.draw.rect(surface, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pg.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple:
        """Возвращает позицию головы змейки - первый элемент в списке
        positions
        """
        return self.positions[0]

    def check_collision(self) -> Optional[bool]:
        """Проверяет столкновение"""
        if self.get_head_position() in self.positions[1:]:
            self.length = self.new_game_length
            self.reset()
            return True
        else:
            return None

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

    def randomize_position(self) -> None:
        """Устанавливает случайное положение яблока на игровом поле"""
        self.position = (
            randint(0, GRID_WIDTH - GRID_SIZE) * GRID_SIZE,
            randint(0, GRID_HEIGHT - GRID_SIZE) * GRID_SIZE
        )

    def draw(self, surface) -> None:
        """Отрисовываю яблоко на игровом поле"""
        rect = pg.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(surface, self.body_color, rect)
        pg.draw.rect(surface, BORDER_COLOR, rect, 1)


def handle_keys(game_object):
    """Функция обработки действий пользователя"""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def had_ate(object_eat, object_eater) -> None:
    """Проверяет события поедания объекта"""
    if object_eat.position == object_eater.get_head_position():
        object_eater.length += 1
        object_eater.draw(screen)
        object_eater.move()

        while True:
            object_eat.randomize_position()
            if object_eat.position not in object_eater.positions:
                break


def main():
    """Выполняется если the_snake запущен напрямую"""
    # Тут нужно создать экземпляры классов.
    snake = Snake(5)
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
        snake.draw(screen)
        apple.draw(screen)
        pg.display.update()


if __name__ == '__main__':
    main()
