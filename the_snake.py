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

TURNING_OPTIONS = {
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
    """Базовый класс игровых объектов."""

    def __init__(self, body_color=None) -> None:
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = body_color

    def draw_one_cell(self, position=None, color=None) -> None:
        """Отрисовывает игровые объекты на игровом поле."""
        # Отрисовка нового сегмента
        if position is None:
            # Когда позиция не передаётся явно
            position = self.position
        if position is None:
            # Бывает так, что стена или кожа еще не определена
            return
        if color is None:
            # Эта строка на мой взгляд нужна для того, чтоб исключить
            # дублирования кода при отрисовки повреждения головы змейки,
            # где передаётся другой цвет.
            color = self.body_color
        rect = pg.Rect((position), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Нужен для тестов."""

    def randomize_position(self, positions) -> None:
        """Устанавливает случайное положение яблока, или стены на игровом поле,
        не занятое другими объектами.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )

            if self.position not in positions:
                break

    def reset(self):
        """Переопределяем аргументы."""
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))


class Snake(GameObject):
    """Класс игровых объектов Змейка"""

    def __init__(self, body_color: tuple = SNAKE_COLOR) -> None:
        super().__init__(body_color)

        self.positions = [self.position]
        self.length = len(self.positions)
        self.direction: tuple = RIGHT
        self.last = None

    def update_direction(self, direction) -> None:
        """Обновляет направления движения змейки после нажатия на кнопку"""
        self.direction = direction

    def move(self) -> None:
        """Обновляет позицию змейки (координаты каждой секции), добавляя новую
        голову в начало списка positions и удаляя последний элемент, если
        длина змейки не увеличилась.
        """
        x_position = (self.position[0]
                      + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        y_position = (self.position[1]
                      + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        self.position = (x_position, y_position)

        past_length: int = len(self.positions)
        self.positions.insert(0, self.position)
        if self.length == past_length:
            self.last = self.positions.pop()
        elif self.length < past_length:
            # Для кожи: сбрасываю кожу, затираю хвост.
            self.last = self.positions.pop()
            self.draw_one_cell()
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Рисуем змейку целеком"""
        # Затирание последнего сегмента.
        if self.last:
            self.draw_one_cell(position=self.last,
                               color=BOARD_BACKGROUND_COLOR)
        # Создаю эффект ползанья змейки.
        for position in self.positions:
            color = (randrange(0, 55, 5), randrange(150, 255, 5), 0)
            self.draw_one_cell(position=position, color=color)
        # Четко рисую голову.
        self.draw_one_cell()

    def draw_damage(self):
        """Рисую клетку, в которой змея получила повреждение"""
        self.draw_one_cell(color=SNAKE_BLOOD_COLOR)
        pg.display.update()

    def get_head_position(self) -> tuple:
        """Возвращает позицию головы змейки - первый элемент в списке
        positions
        """
        return self.positions[0]

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
        super().reset()
        self.positions = [self.position]
        self.length = len(self.positions)
        self.direction = RIGHT


class Apple(GameObject):
    """Класс игровых объектов Яблоко"""

    def __init__(self, body_color: tuple = APPLE_COLOR) -> None:
        super().__init__(body_color)
        # Начальная позиция всех объектов, если она не переопределена, в том
        # числе голова змейки. Передовать объект змейка нет необходимости.
        self.randomize_position([self.position]) 
        # Теперь метод .randomize_position() в родительском классе

    def reset(self):
        """Задаю первое яблоко, таким образом, чтоб оно точно не стояло на
        змейке.
        """
        super().reset()
        self.randomize_position([self.position])

    def draw(self):
        """Рисую яблоко"""
        super().draw_one_cell()


class Skins(GameObject):
    """Класс игровых объектов Кожа."""

    def __init__(self, body_color: tuple = SKIN_COLOR) -> None:
        super().__init__(body_color)
        self.position = None
        self.positions = set()

    def add_skin(self, position):
        """Добавляет сброшенную кожу"""
        self.position = position
        self.positions.add(self.position)

    def draw(self):
        """Рисую сброшенную кожу, которая всегда остаётся за змейкой,
        и никогда не стоит на Змейке, которая стоит на Яблоке
        """
        for self.position in self.positions:
            super().draw_one_cell()
        # Когда змейка съедает кожу, она травится, и сбрасывает
        # в два раза больше кожи. Геймплеейно, так интересней.

    def reset(self):
        """Отчищает множество позиций"""
        super().reset()
        self.position = None
        self.positions = set()


class Walls(GameObject):
    """Класс игровых объектов Яблоко"""

    def __init__(self, body_color: tuple = WALLS_COLOR) -> None:
        super().__init__(body_color)
        self.positions = list()
        self.position = None

    def randomize_position(self, positions) -> None:
        """Устанавливает случайное положение стены на игровом поле"""
        super().randomize_position(positions)
        self.positions.append(self.position)

    def reset(self):
        """Отчищает множество позиций"""
        super().reset()
        self.position = None
        self.positions = list()

    def draw(self):
        """Рисую стену, если она есть, которая не стоит на Яблоке,
        которое не стоит на Змейке.
        """
        super().draw_one_cell()


def ate(snake, apple, skin, walls):
    """Проверяет события поедания объекта"""
    # Я непонимяю что я делаю вне объекта змейка, кроме Змейки никто в
    # кушает.
    last = snake.last
    if apple.position == snake.get_head_position():
        snake.length += 1
        list_positions = busy_positions(
            snake, *(snake.positions, skin.positions, walls.positions)
        )
        apple.randomize_position(list_positions)
        # Каждые 5 яблок ускоряют метоболизм змейки
        # Змейка сбрасывает кожу
        if not snake.length % 5:
            skin.add_skin(last)
        # После того как змейка станет больше 5 ячеек
        # её начинают ограничивать стены каждый раз,
        # как она выростает на 2 ячейки
        if not snake.length % 2 and snake.length > 5:
            walls.randomize_position(list_positions)

    for skin_position in list(skin.positions):
        if skin_position == snake.get_head_position():
            snake.length -= 1
            if not snake.length:
                skin.positions = set()
                snake.draw_damage()
                return False
            skin.positions.discard(snake.get_head_position())
            skin.add_skin(snake.positions[-2])
            skin.add_skin(snake.positions[-1])
    return True


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

            elif event.key in TURNING_OPTIONS[game_object.direction]:
                direction = TURNING_OPTIONS[game_object.direction][event.key]
                return game_object.update_direction(direction)


def pressed_shift():
    """Возвращает коэфициент ускорения"""
    keys = pg.key.get_pressed()
    if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
        return ACCELERATION
    return 1


def draw(*args):
    """Рисуем всё"""
    for game_object in args:
        game_object.draw()


def restart(*args):
    """Перезапуск"""
    for game_object in args:
        game_object.reset()
    screen.fill(BOARD_BACKGROUND_COLOR)


def main():
    """Выполняется если the_snake запущен напрямую"""
    snake = Snake()
    apple = Apple()
    # Яблоко ставится куда угодно, но не на змейку
    skin = Skins()
    walls = Walls()
    # Никто тут не на кого не встаёт, все позиции определяются
    # тогда, когда должны определяться busy_positions()

    points = 0
    max_points = 0

    while True:
        # Изменение скорости с ростом змейки
        # на 1 за 5 съеденных яблок
        game_speed = (SPEED + snake.length // 5) * pressed_shift()
        clock.tick(game_speed)

        handle_keys(snake)
        snake.move()
        if not ate(snake, apple, skin, walls) or snake.check_collision(walls):
            clock.tick(1)
            restart(snake, apple, skin, walls)
            points = 0
            continue
        draw(snake, apple, skin, walls)

        points = snake.length
        max_points = max(max_points, points)
        pg.display.set_caption(
            "Змейка. Выход - ESC.  "
            f"Длина змейки: {points}. Рекорд: {max_points}  "
            f"SHIFT - ускорение."
        )
        pg.display.update()


if __name__ == "__main__":
    main()
