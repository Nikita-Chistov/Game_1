import math

from matplotlib.pyplot import figure

from settings import *
import numpy as np
import pygame
import os
import sys
import random
from PIL import Image
import pygame_gui

pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
pygame.display.set_caption('RTKY')
display_info = pygame.display.Info()
size = width, height = (display_info.current_w, display_info.current_h)
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
font = pygame.font.SysFont(None, 30)
no_effectiveness_update = True
render_count = 0
all_sprites = pygame.sprite.Group()
phantom_bilds = pygame.sprite.Group()


def get_resize_images(name, standart_size=(1, 1)):
    images = {}
    for size in range(MIN_CELL_SIZE - ZOOM_SPEED, MAX_CELL_SIZE + ZOOM_SPEED, ZOOM_SPEED):
        size_images = []
        for root, _, files in os.walk(os.path.join("Data", "Sprites", name)):
            sort_files = sorted(files, key=lambda x: int(x.split('.')[0].split('_')[-1]))
            for image_name in sort_files:
                image_path = os.path.join(root, image_name)
                image = load_image(image_path)
                pil_image = Image.frombytes('RGBA', image.get_size(), pygame.image.tobytes(image, 'RGBA'))
                resized_image = pil_image.resize((size * standart_size[0], size * standart_size[1]), Image.LANCZOS)
                resized_surface = pygame.image.frombytes(resized_image.tobytes(), resized_image.size, 'RGBA')
                resized_surface = resized_surface.convert_alpha()
                orientation_images = []
                for orientation in range(4):
                    orientation_images.append(pygame.transform.rotate(resized_surface, orientation * -90))
                size_images.append(orientation_images)
        images[size] = size_images
    return images


def red_filter(image):
    width, height = image.get_size()
    for x in range(width):
        for y in range(height):
            r, g, b, a = image.get_at((x, y))
            red = (r + g + b) // 3
            image.set_at((x, y), (red, 0, 0, a))


def load_image(path, colorkey=None):
    # если файл не существует, то выходим
    if not os.path.isfile(path):
        print(f"Файл с изображением '{path}' не найден")
        sys.exit()
    image = pygame.image.load(path)
    if colorkey is not None:
        image = image.convert_alpha()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


class Data:
    def __init__(self):
        self.figures_all_levels = [
            np.array([
                [(2, 0, 195, 205, 236), (1, 1, 195, 205, 236)],
                [(2, 3, 195, 205, 236), (1, 2, 195, 205, 236)]]),
            np.array([
                [(0, 0, 195, 205, 236), (1, 1, 195, 205, 236)],
                [(0, 0, 195, 205, 236), (1, 2, 195, 205, 236)]]),
            np.array([
                [(1, 0, 195, 205, 236), (1, 1, 195, 205, 236)],
                [(1, 3, 195, 205, 236), (2, 2, 195, 205, 236)]]),
            np.array([
                [(1, 3, 195, 205, 236), (1, 0, 195, 205, 236)],
                [(1, 2, 195, 205, 236), (1, 1, 195, 205, 236)]]),
            np.array([
                [(1, 0, 195, 205, 236), (1, 1, 195, 205, 236), (1, 0, 195, 205, 236), (1, 1, 195, 205, 236)],
                [(1, 3, 195, 205, 236), (2, 2, 195, 205, 236), (2, 3, 195, 205, 236), (1, 2, 195, 205, 236)],
                [(1, 0, 195, 205, 236), (2, 1, 195, 205, 236), (2, 0, 195, 205, 236), (1, 1, 195, 205, 236)],
                [(1, 3, 195, 205, 236), (1, 2, 195, 205, 236), (1, 3, 195, 205, 236), (1, 2, 195, 205, 236)]
            ]),
        ]
        self.count_all_levels = [10, 20, 50, 100, 100]
        self.level = 0
        self.bildings_count_levels = [100, 200, 500]
        self.bildings_levels = {
            Factory: [0, [250, 200, 150, 100]],
            Spliter: [0, [250, 200, 150, 100]],
            Connector: [0, [250, 200, 150, 100]],
            Rotator: [0, [250, 200, 150, 100]],
            Painting: [0, [250, 200, 150, 100]],
            Asembler: [0, [250, 200, 150, 100]],
        }
        self.figures_in_hub = {}
        self.font = pygame.font.SysFont(None, 30)
    def update_level(self, bild):
        update_figure = np.array([])
        level = self.bildings_levels[bild][0]
        if self.bildings_count_levels[level] <= self.figures_in_hub.get(str(update_figure), 0):
            self.figures_in_hub[str(update_figure)] -= self.bildings_count_levels[level]
            self.bildings_levels[bild][0] += 1
            bild.Patern_delays[-1] = self.bildings_levels[bild][1][self.bildings_levels[bild][0]]


    def get_figure(self, figure):
        self.figures_in_hub[str(figure)] = self.figures_in_hub.get(str(figure), 0) + 1
        if self.figures_in_hub.get(str(self.figures_all_levels[self.level]), 0) >= self.count_all_levels[self.level]:
            self.level += 1

    def render_part_circle(self, x, y, size, orientation, color):
        radius = size
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        pygame.draw.circle(surf, (0, 0, 0), (radius, radius), radius)
        if size < 10:
            pygame.draw.circle(surf, color, (radius, radius), radius - 1)
            pygame.draw.line(surf, (0, 0, 0), (radius, 0), (radius, radius * 2), 1)
            pygame.draw.line(surf, (0, 0, 0), (0, radius), (radius * 2, radius), 1)
        else:
            pygame.draw.circle(surf, color, (radius, radius), radius - 2)
            pygame.draw.line(surf, (0, 0, 0), (radius - 1, 0), (radius - 1, radius * 2), 2)
            pygame.draw.line(surf, (0, 0, 0), (0, radius - 1), (radius * 2, radius - 1), 2)
        if orientation == 0:
            mask_rect = pygame.Rect(0, 0, radius, radius)
        elif orientation == 1:
            mask_rect = pygame.Rect(radius, 0, radius, radius)
        elif orientation == 2:
            mask_rect = pygame.Rect(radius, radius, radius, radius)
        elif orientation == 3:
            mask_rect = pygame.Rect(0, radius, radius, radius)
        surf = surf.subsurface(mask_rect)
        screen.blit(surf, (x, y))

    def render_part_square(self, x, y, size, orientation, color):
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, size * 2, size * 2))
        if size < 10:
            pygame.draw.rect(surf, color, (1, 1, size * 2 - 2, size * 2 - 2))
            pygame.draw.line(surf, (0, 0, 0), (size, 0), (size, size * 2), 1)
            pygame.draw.line(surf, (0, 0, 0), (0, size), (size * 2, size), 1)
        else:
            pygame.draw.rect(surf, color, (2, 2, size * 2 - 4, size * 2 - 4))
            pygame.draw.line(surf, (0, 0, 0), (size - 1, 0), (size - 1, size * 2), 2)
            pygame.draw.line(surf, (0, 0, 0), (0, size - 1), (size * 2, size - 1), 2)
        if orientation == 0:
            mask_rect = pygame.Rect(0, 0, size, size)
        elif orientation == 1:
            mask_rect = pygame.Rect(size, 0, size, size)
        elif orientation == 2:
            mask_rect = pygame.Rect(size, size, size, size)
        elif orientation == 3:
            mask_rect = pygame.Rect(0, size, size, size)
        surf = surf.subsurface(mask_rect)
        screen.blit(surf, (x, y))

    def draw(self, screen):
        pygame.draw.rect(screen, (50, 50, 50), (10, 10, 250, 80))
        pygame.draw.rect(screen, (200, 200, 200), (10, 10, 250, 80), 2)

        level_text = self.font.render(f"Уровень: {self.level + 1}", True, (255, 255, 255))
        screen.blit(level_text, (20, 20))

        figures_text = self.font.render(
            f"{self.figures_in_hub.get(str(self.figures_all_levels[self.level]), 0)}/{self.count_all_levels[self.level]}",
            True,
            (255, 255, 255))
        screen.blit(figures_text, (20, 50))

        figure = self.figures_all_levels[self.level]
        centre = (200, 50)
        # pygame.draw.rect(screen, (122, 0, 122), (self.x * self.board.cell_size + self.board.x, self.y * self.board.cell_size + self.board.y,self.board.cell_size, self.board.cell_size))
        part_size = 100 // 2 // figure.shape[0]
        x_n = part_size * figure.shape[0] // 2
        y_n = part_size * figure.shape[0] // 2
        for i in range(figure.shape[0]):
            for j in range(figure.shape[0]):
                if figure[j, i] is not None:
                    if figure[j, i][0] == 1:
                        self.render_part_circle(centre[0] - x_n + part_size * i, centre[1] - y_n + part_size * j,
                                                part_size, figure[j, i][1], figure[j, i][2:5])
                    if figure[j, i][0] == 2:
                        self.render_part_square(centre[0] - x_n + part_size * i, centre[1] - y_n + part_size * j,
                                                part_size, figure[j, i][1], figure[j, i][2:5])

    def save(self):
        with open(f"game_data.txt", "w") as f:
            f.write(str(self.figures_in_hub))
            f.write("\n")
            f.write(str(self.level))

    def load(self):
        with open(f"game_data.txt", "r") as f:
            self.figures_in_hub = eval(f.readline())
            self.level = eval(f.readline())


class Bildings(pygame.sprite.Sprite):
    Sprite_images = get_resize_images("conv")
    Size = (1, 1)
    Patern_delays = []
    Patern_images = []
    capture = 0
    current_sprite = 0
    Sprite_group = pygame.sprite.Group()
    Speed = 1
    Inputs = np.array([[0]])
    Numbes_cells = np.array([[1]])
    Input_Figures = np.array([["11 11"]])
    Outputs = np.array([[1]])
    Size_input_Figures = [2]
    Inputs_orientation = np.array([[0]])

    @classmethod
    def Update_animation(cls):
        cls.capture = (cls.capture + cls.Speed) % (cls.Patern_delays[-1] + 1)
        if cls.capture in cls.Patern_delays:
            cls.current_sprite = cls.Patern_images[cls.Patern_delays.index(cls.capture)]
        if cls.capture == cls.Patern_delays[-1]:
            for sprite in cls.Sprite_group:
                sprite.have_figure = sprite.check_can_create()
                if sprite.have_figure:
                    sprite.create_product()

    def create_product(self):
        pass

    def __init__(self, board, x, y, orientation):
        super().__init__(all_sprites)
        self.__class__.Sprite_group.add(self)
        self.x = x
        self.y = y
        self.orientation = orientation
        self.board = board
        self.rect = pygame.Rect(0, 0, self.Size[0] * self.board.cell_size, self.Size[1] * self.board.cell_size)
        self.update_image()
        board.board[self.y][self.x] = self
        self.inputs = {}
        self.outputs = {}
        if orientation % 2 == 0:
            size = self.Size
        else:
            size = (self.Size[1], self.Size[0])
        inputs = np.rot90(self.Inputs, 4 - orientation)
        outputs = np.rot90(self.Outputs, 4 - orientation)
        inputs_figures = np.rot90(self.Input_Figures, 4 - orientation)
        numbers_cell = np.rot90(self.Numbes_cells, 4 - orientation)
        inputs_orientation = np.rot90(self.Inputs_orientation.copy(), 4 - orientation)
        for i in range(size[0]):
            for j in range(size[1]):
                inputs_orientation[j][i] = (inputs_orientation[j][i] + orientation) % 4
        for i in range(size[0]):
            for j in range(size[1]):
                self.board.board[self.y + j][self.x + i] = self
                if inputs[j][i] == 1:
                    self.inputs[(self.x + i, self.y + j)] = (
                        numbers_cell[j][i], inputs_figures[j][i], inputs_orientation[j][i])
                if outputs[j][i] == 1:
                    self.outputs[(self.x + i, self.y + j)] = numbers_cell[j][i]
        self.inputs = dict(sorted(self.inputs.items(), key=lambda x: x[1][0]))
        self.outputs = dict(sorted(self.outputs.items(), key=lambda x: x[1]))

    def check_can_create(self):
        return all([self.board.figures_on_board[y][x] is not None for x, y in self.inputs.keys()]) and all(
            [self.board.figures_on_board[y][x].in_bilding for x, y in self.inputs.keys()])

    def update_image(self):
        self.image = self.Sprite_images[self.board.cell_size][self.current_sprite][self.orientation]

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEBUTTONDOWN and (args[0].button == 4 or args[0].button == 5):
                self.update_image()
        self.rect.x = self.x * self.board.cell_size + self.board.x
        self.rect.y = self.y * self.board.cell_size + self.board.y
        self.update_image()

    def kill(self):
        self.__class__.Sprite_group.remove(self)
        self.board.board[self.y][self.x] = None
        if self.orientation % 2 == 0:
            size = self.Size
        else:
            size = (self.Size[1], self.Size[0])
        for i in range(size[0]):
            for j in range(size[1]):
                self.board.board[self.y + j][self.x + i] = None


class Belt(Bildings):
    Sprite_images = get_resize_images("Belt")
    Sprite_group = pygame.sprite.Group()
    Size = (1, 1)
    Patern_delays = list(range(0, 100, 1))
    Patern_images = list(range(0, 100, 1))
    # Patern_delays = [0, 10]
    # Patern_images = [0, 50]
    capture = 0
    current_sprite = 0
    Speed = BELT_SPEED

    def check_can_create(self):
        return True


class BeltLeft(Belt):
    Sprite_images = get_resize_images("BeltLeft")
    Sprite_group = pygame.sprite.Group()


class BeltRight(Belt):
    Sprite_images = get_resize_images("BeltRight")
    Sprite_group = pygame.sprite.Group()


class BeltConnector(Bildings):
    Size = (2, 1)
    Sprite_images = get_resize_images("BeltConnector", Size)
    Sprite_group = pygame.sprite.Group()
    Patern_delays = [0, 50]
    Patern_images = [0, 0]
    capture = 0
    current_sprite = 0
    Speed = 1
    Numbes_cells = np.array([[1, 2]])
    Inputs = np.array([[1, 1]])
    Inputs_orientation = np.array([[0, 0]])
    Input_Figures = np.array([["11 11", "11 11"]])
    Outputs = np.array([[1, 0]])
    Size_input_Figures = [2, 4]

    def check_can_create(self):
        return any(
            [self.board.figures_on_board[y][x] is not None and self.board.figures_on_board[y][x].in_bilding for x, y in
             self.inputs.keys()])

    def create_product(self):
        x_output, y_output = list(self.outputs.keys())[0]
        for x, y in self.inputs.keys():
            if self.board.figures_on_board[y][x] is not None:
                if x == x_output and y == y_output:
                    self.board.figures_on_board[y][x].in_bilding = False
                    self.board.figures_on_board[y][x].f_render = True
                    self.board.figures_on_board[y][x].stop = False
                else:
                    if self.board.figures_on_board[y_output][x_output] is None:
                        figure = self.board.figures_on_board[y][x].componets
                        self.board.figures_on_board[y][x] = None
                        Figure(2, self.board, x_output, y_output, figure)


class Factory(Bildings):
    Sprite_images = get_resize_images("Factory")
    Sprite_group = pygame.sprite.Group()
    Size = (1, 1)
    Patern_delays = [0, 300]
    Patern_images = [0, 0]
    capture = 0
    current_sprite = 0
    Speed = 1
    Inputs = np.array([[0]])
    Numbes_cells = np.array([[1]])
    Input_Figures = np.array([["11 11"]])
    Outputs = np.array([[1]])
    Size_input_Figures = [2]
    Inputs_orientation = np.array([[0]])

    def check_can_create(self):
        return self.board.figures_on_board[self.y][self.x] is None

    def create_product(self):
        self.board.figures_on_board[self.y][self.x] = Figure(2, self.board, self.x, self.y, np.array([
            [(2, 0, 195, 205, 236), (1, 1, 195, 205, 236)],
            [(2, 3, 195, 205, 236), (1, 2, 195, 205, 236)]
        ]))


class Hub(Bildings):
    Size = (3, 3)
    Sprite_images = get_resize_images("Hub", Size)
    Sprite_group = pygame.sprite.Group()
    Patern_delays = [0, 50]
    Patern_images = [0, 0]
    capture = 0
    current_sprite = 0
    Speed = 1
    Numbes_cells = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    Inputs = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    Input_Figures = np.array([["", "11 11", ""], ["11 11", "", "11 11"], ["", "11 11", ""]])
    Inputs_orientation = np.array([[0, 2, 0], [1, 0, 3], [0, 0, 0]])
    Outputs = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    Size_input_Figures = [2, 4]

    def check_can_create(self):
        return any(
            [self.board.figures_on_board[y][x] is not None and self.board.figures_on_board[y][x].in_bilding for x, y in
             self.inputs.keys()])

    def create_product(self):
        global data
        for x, y in self.inputs.keys():
            if self.board.figures_on_board[y][x] is not None:
                figure = self.board.figures_on_board[y][x].componets
                data.get_figure(figure)
                self.board.figures_on_board[y][x].kill()


class Spliter(Bildings):
    Size = (2, 1)
    Sprite_images = get_resize_images("Spliter", Size)
    Sprite_group = pygame.sprite.Group()
    Patern_delays = [0, 250]
    Patern_images = [0, 0]
    capture = 0
    current_sprite = 0
    Speed = 1
    Numbes_cells = np.array([[1, 2]])
    Inputs = np.array([[1, 0]])
    Inputs_orientation = np.array([[0, 0]])
    Input_Figures = np.array([["11 11", ""]])
    Outputs = np.array([[1, 1]])
    Size_input_Figures = [2]

    def check_can_create(self):
        x, y = list(self.outputs.items())[1][0]
        return super().check_can_create() and self.board.figures_on_board[y][x] is None

    def create_product(self):
        x_input = list(self.inputs.items())[0][0][0]
        y_input = list(self.inputs.items())[0][0][1]
        figure = self.board.figures_on_board[y_input][x_input].componets
        self.board.figures_on_board[y_input][x_input] = None
        zero_figure = np.array([
            [(0, 0, 195, 205, 236), (0, 0, 195, 205, 236)],
            [(0, 0, 195, 205, 236), (0, 0, 195, 205, 236)]
        ])
        zero_figure_left, zero_figure_right = np.hsplit(zero_figure, 2)
        figure_left, figure_right = np.hsplit(figure, 2)
        figure_left = np.concatenate((figure_left, zero_figure_right), axis=1)
        figure_right = np.concatenate((zero_figure_left, figure_right), axis=1)
        output_x_1 = list(self.outputs.items())[0][0][0]
        output_y_1 = list(self.outputs.items())[0][0][1]
        output_x_2 = list(self.outputs.items())[1][0][0]
        output_y_2 = list(self.outputs.items())[1][0][1]
        Figure(2, self.board, output_x_1, output_y_1, figure_left)
        Figure(2, self.board, output_x_2, output_y_2, figure_right)


class Deleter(Bildings):
    Size = (1, 1)
    Sprite_images = get_resize_images("Deleter", Size)
    Sprite_group = pygame.sprite.Group()
    Patern_delays = [0, 50]
    Patern_images = [0, 0]
    capture = 0
    current_sprite = 0
    Speed = 1
    Numbes_cells = np.array([[1]])
    Inputs = np.array([[1]])
    Inputs_orientation = np.array([[0]])
    Input_Figures = np.array([["11 11"]])
    Outputs = np.array([[0]])
    Size_input_Figures = [2, 4]

    def check_can_create(self):
        return True

    def create_product(self):
        x_input = list(self.inputs.items())[0][0][0]
        y_input = list(self.inputs.items())[0][0][1]
        self.board.figures_on_board[y_input][x_input] = None


class Connector(Bildings):
    Size = (2, 1)
    Sprite_images = get_resize_images("Сonneсtor", Size)
    Sprite_group = pygame.sprite.Group()
    Patern_delays = [0, 250]
    Patern_images = [0, 0]
    capture = 0
    current_sprite = 0
    Speed = 1
    Numbes_cells = np.array([[1, 2]])
    Inputs = np.array([[1, 1]])
    Inputs_orientation = np.array([[0, 0]])
    Input_Figures = np.array([["10 10", "01 01"]])
    Outputs = np.array([[1, 0]])
    Size_input_Figures = [2]

    def create_product(self):
        x_input_1 = list(self.inputs.items())[0][0][0]
        y_input_1 = list(self.inputs.items())[0][0][1]
        x_input_2 = list(self.inputs.items())[1][0][0]
        y_input_2 = list(self.inputs.items())[1][0][1]
        figure_left = self.board.figures_on_board[y_input_1][x_input_1].componets
        figure_right = self.board.figures_on_board[y_input_2][x_input_2].componets
        self.board.figures_on_board[y_input_1][x_input_1] = None
        self.board.figures_on_board[y_input_2][x_input_2] = None
        figure_left = np.hsplit(figure_left, 2)[0]
        figure_right = np.hsplit(figure_right, 2)[1]
        figure = np.concatenate((figure_left, figure_right), axis=1)
        x_output = list(self.outputs.items())[0][0][0]
        y_output = list(self.outputs.items())[0][0][1]
        Figure(2, self.board, x_output, y_output, figure)


class Rotator(Bildings):
    Size = (1, 1)
    Sprite_images = get_resize_images("Rotator", Size)
    Sprite_group = pygame.sprite.Group()
    Patern_delays = [0, 250]
    Patern_images = [0, 0]
    capture = 0
    current_sprite = 0
    Speed = 1
    Numbes_cells = np.array([[1]])
    Inputs = np.array([[1]])
    Inputs_orientation = np.array([[0]])
    Input_Figures = np.array([["11 11"]])
    Outputs = np.array([[0]])
    Size_input_Figures = [2]

    def create_product(self):
        x_input = list(self.inputs.items())[0][0][0]
        y_input = list(self.inputs.items())[0][0][1]
        figure = self.board.figures_on_board[y_input][x_input].componets
        figure = np.rot90(figure, 3)
        for i in range(figure.shape[0]):
            for j in range(figure.shape[1]):
                figure[i][j][1] = (figure[i][j][1] + 1) % 4
        Figure(2, self.board, x_input, y_input, figure)


class Painting(Bildings):
    Size = (2, 2)
    Sprite_images = get_resize_images("Painting", Size)
    Patern_delays = [0, 250]
    Patern_images = [0, 0]
    capture = 0
    current_sprite = 0
    Speed = 1
    Inputs = np.array([[0, 0], [1, 0]])
    Inputs_orientation = np.array([[0, 0], [0, 0]])
    Numbes_cells = np.array([[1, 2], [3, 4]])
    Input_Figures = np.array([["", ""], ["11 11", ""]])
    Outputs = np.array([[0, 1], [0, 0]])
    Size_input_Figures = [2]
    Sprite_group = pygame.sprite.Group()

    def __init__(self, board, x, y, orientation):
        super().__init__(board, x, y, orientation)
        self.colour = ""

    def check_can_create(self):
        x, y = list(self.outputs.items())[0][0]
        return super().check_can_create() and self.board.figures_on_board[y][x] is None

    def create_product(self):
        x_input = list(self.inputs.items())[0][0][0]
        y_input = list(self.inputs.items())[0][0][1]
        figure = self.board.figures_on_board[y_input][x_input].componets
        new_color = (255, 0, 0)
        for row in range(figure.shape[0]):
            for col in range(figure.shape[1]):
                figure[row, col][2:] = new_color
        x_output = list(self.outputs.items())[0][0][0]
        y_output = list(self.outputs.items())[0][0][1]
        Figure(2, self.board, x_output, y_output, figure)
        self.board.figures_on_board[y_input][x_input] = None


class Asembler(Bildings):
    Size = (2, 2)
    Sprite_images = get_resize_images("Asembler", Size)
    Sprite_group = pygame.sprite.Group()
    Patern_delays = [0, 250]
    Patern_images = [0, 0]
    capture = 0
    current_sprite = 0
    Speed = 1
    Numbes_cells = np.array([[1, 2], [3, 4]])
    Inputs = np.array([[1, 1], [1, 1]])
    Inputs_orientation = np.array([[1, 3], [1, 3]])
    Input_Figures = np.array([["11 11", "11 11"], ["11 11", "11 11"]])
    Outputs = np.array([[1, 0], [0, 0]])
    Size_input_Figures = [2]

    def create_product(self):
        input_cord = [(y, x) for x, y in self.inputs.keys()]
        figure1 = self.board.figures_on_board[input_cord[0][0]][input_cord[0][1]].componets
        figure2 = self.board.figures_on_board[input_cord[1][0]][input_cord[1][1]].componets
        figure3 = self.board.figures_on_board[input_cord[2][0]][input_cord[2][1]].componets
        figure4 = self.board.figures_on_board[input_cord[3][0]][input_cord[3][1]].componets
        for y, x in input_cord:
            self.board.figures_on_board[y][x] = None
        up = np.concatenate((figure1, figure2), axis=1)
        down = np.concatenate((figure3, figure4), axis=1)
        new_figure = np.concatenate((up, down), axis=0)
        x_output = list(self.outputs.items())[0][0][0]
        y_output = list(self.outputs.items())[0][0][1]
        Figure(4, self.board, x_output, y_output, new_figure)


class Figure:
    сurrent_pos = 0
    all_figures = []

    @classmethod
    def Update(cls):
        cls.сurrent_pos = (cls.сurrent_pos + BELT_SPEED) % 100
        if cls.сurrent_pos == 0:
            for figure in cls.all_figures:
                figure.update_pos_on_board()
        elif cls.сurrent_pos == 50:
            for figure in cls.all_figures:
                figure.check_can_render()
                figure.new_orientation()

    def __init__(self, size, board, x, y, figure: np.array):

        self.size = size
        self.componets = figure
        self.board = board
        self.x = x
        self.y = y
        self.board.figures_on_board[self.y][self.x] = self
        self.x_in_cell = 0
        self.y_in_cell = 0
        self.new_orientation()
        self.all_figures.append(self)
        self.stop = False
        self.in_bilding = False
        self.f_render = False
        patern = []
        for i in range(self.size):
            for j in range(self.size):
                if self.componets[i][j][0] != 0:
                    patern.append("1")
                else:
                    patern.append("0")
            patern.append(" ")
        self.patern = "".join(patern[:-1])
        if all([s in ('0', ' ') for s in self.patern]):
            self.kill()

    def kill(self):
        self.board.figures_on_board[self.y][self.x] = None
        del self.all_figures[self.all_figures.index(self)]

    def new_orientation(self):
        if self.board.board[self.y][self.x] is None:
            self.kill()
        else:
            if self.board.board[self.y][self.x].orientation == 0:
                self.update_x_y = (0, -1, 0, 100, 1, 0)
            elif self.board.board[self.y][self.x].orientation == 1:
                self.update_x_y = (1, 0, 0, 0, 0, 1)
            elif self.board.board[self.y][self.x].orientation == 2:
                self.update_x_y = (0, 1, 0, 0, 1, 0)
            elif self.board.board[self.y][self.x].orientation == 3:
                self.update_x_y = (-1, 0, 100, 0, 0, 1)
            self.orientation = self.board.board[self.y][self.x].orientation

    def check_patern(self, patern):
        if len(patern.split(" ")) != self.size:
            return False
        for i in range(self.size):
            for j in range(self.size):
                if patern.split(" ")[i][j] == "0" and self.patern.split(" ")[i][j] == "1":
                    return False
        return True

    def check_can_render(self):
        if not self.in_bilding:
            self.f_render = True
        else:
            self.f_render = False

    def update_pos_on_board(self):
        if not self.in_bilding:
            if self.__class__.сurrent_pos == 0 or self.__class__.сurrent_pos != 0 and self.stop:
                next_x = self.x + self.update_x_y[0]
                next_y = self.y + self.update_x_y[1]
                f = False
                if self.board.board[next_y][next_x].__class__ is Belt:
                    if self.board.board[next_y][next_x].orientation == self.orientation:
                        if self.board.figures_on_board[next_y][next_x] is None:
                            f = True
                        else:
                            if not self.board.figures_on_board[next_y][next_x].stop:
                                f = True
                elif self.board.board[next_y][next_x].__class__ is BeltLeft:
                    if (self.board.board[next_y][next_x].orientation + 1) % 4 == self.orientation:
                        if self.board.figures_on_board[next_y][next_x] is None:
                            f = True
                        else:
                            if not self.board.figures_on_board[next_y][next_x].stop:
                                f = True
                elif self.board.board[next_y][next_x].__class__ is BeltRight:
                    if (self.board.board[next_y][next_x].orientation + 3) % 4 == self.orientation:
                        if self.board.figures_on_board[next_y][next_x] is None:
                            f = True
                        else:
                            if not self.board.figures_on_board[next_y][next_x].stop:
                                f = True
                elif self.board.board[next_y][next_x].__class__.__bases__[0] is Bildings:
                    if self.board.figures_on_board[next_y][next_x] is None:
                        if (next_x, next_y) in self.board.board[next_y][next_x].inputs.keys():
                            if self.check_patern(
                                    self.board.board[next_y][next_x].inputs[(next_x, next_y)][1]) or str(
                                self.board.board[next_y][next_x].__class__) in (
                                    "<class '__main__.Deleter'>", "<class '__main__.Hub'>"):
                                if self.orientation == self.board.board[next_y][next_x].inputs[(next_x, next_y)][2]:
                                    f = True
                                    self.in_bilding = True
                                    self.stop = True
                if f:
                    self.stop = False
                    if self.board.figures_on_board[self.y][self.x] == self:
                        self.board.figures_on_board[self.y][self.x] = None
                    self.x += self.update_x_y[0]
                    self.y += self.update_x_y[1]
                    self.board.figures_on_board[self.y][self.x] = self
                else:
                    self.stop = True

    def render_part_circle(self, x, y, size, orientation, color):
        radius = size
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        pygame.draw.circle(surf, (0, 0, 0), (radius, radius), radius)
        if size < 10:
            pygame.draw.circle(surf, color, (radius, radius), radius - 1)
            pygame.draw.line(surf, (0, 0, 0), (radius, 0), (radius, radius * 2), 1)
            pygame.draw.line(surf, (0, 0, 0), (0, radius), (radius * 2, radius), 1)
        else:
            pygame.draw.circle(surf, color, (radius, radius), radius - 2)
            pygame.draw.line(surf, (0, 0, 0), (radius - 1, 0), (radius - 1, radius * 2), 2)
            pygame.draw.line(surf, (0, 0, 0), (0, radius - 1), (radius * 2, radius - 1), 2)
        if orientation == 0:
            mask_rect = pygame.Rect(0, 0, radius, radius)
        elif orientation == 1:
            mask_rect = pygame.Rect(radius, 0, radius, radius)
        elif orientation == 2:
            mask_rect = pygame.Rect(radius, radius, radius, radius)
        elif orientation == 3:
            mask_rect = pygame.Rect(0, radius, radius, radius)
        surf = surf.subsurface(mask_rect)
        screen.blit(surf, (x, y))

    def render_part_square(self, x, y, size, orientation, color):
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, size * 2, size * 2))
        if size < 10:
            pygame.draw.rect(surf, color, (1, 1, size * 2 - 2, size * 2 - 2))
            pygame.draw.line(surf, (0, 0, 0), (size, 0), (size, size * 2), 1)
            pygame.draw.line(surf, (0, 0, 0), (0, size), (size * 2, size), 1)
        else:
            pygame.draw.rect(surf, color, (2, 2, size * 2 - 4, size * 2 - 4))
            pygame.draw.line(surf, (0, 0, 0), (size - 1, 0), (size - 1, size * 2), 2)
            pygame.draw.line(surf, (0, 0, 0), (0, size - 1), (size * 2, size - 1), 2)
        if orientation == 0:
            mask_rect = pygame.Rect(0, 0, size, size)
        elif orientation == 1:
            mask_rect = pygame.Rect(size, 0, size, size)
        elif orientation == 2:
            mask_rect = pygame.Rect(size, size, size, size)
        elif orientation == 3:
            mask_rect = pygame.Rect(0, size, size, size)
        surf = surf.subsurface(mask_rect)
        screen.blit(surf, (x, y))

    def render(self):
        if self.f_render:
            centre = (self.x * self.board.cell_size + self.board.x + (
                    self.x_in_cell + 50 * self.update_x_y[4]) * self.board.cell_size // 100,
                      self.y * self.board.cell_size + self.board.y + (
                              self.y_in_cell + 50 * self.update_x_y[5]) * self.board.cell_size // 100)
            # pygame.draw.rect(screen, (122, 0, 122), (self.x * self.board.cell_size + self.board.x, self.y * self.board.cell_size + self.board.y,self.board.cell_size, self.board.cell_size))
            part_size = self.board.cell_size // 2 // self.size
            x_n = part_size * self.size // 2
            y_n = part_size * self.size // 2
            for i in range(self.size):
                for j in range(self.size):
                    if self.componets[j, i] is not None:
                        if self.componets[j, i][0] == 1:
                            self.render_part_circle(centre[0] - x_n + part_size * i, centre[1] - y_n + part_size * j,
                                                    part_size, self.componets[j, i][1], self.componets[j, i][2:5])
                        if self.componets[j, i][0] == 2:
                            self.render_part_square(centre[0] - x_n + part_size * i, centre[1] - y_n + part_size * j,
                                                    part_size, self.componets[j, i][1], self.componets[j, i][2:5])

    def update_pos(self):
        if not self.stop:
            self.x_in_cell = (self.update_x_y[2] + self.update_x_y[0] * self.__class__.сurrent_pos)
            self.y_in_cell = (self.update_x_y[3] + self.update_x_y[1] * self.__class__.сurrent_pos)


code_bildings = {
    Belt: BELT_CODE,
    BeltRight: BELT_RIGHT_CODE,
    BeltLeft: BELT_LEFT_CODE,
    Factory: FACTORY_CODE,
    Hub: HUB_CODE,
    Spliter: SPLITTER_CODE,
    Deleter: DELETER_CODE,
    Connector: CONNECTOR_CODE,
    Rotator: ROTATOR_CODE,
    Painting: PAINTING_CODE

}


class Board:
    def __init__(self, width, height, cell_size=40):
        self.width = width
        self.height = height
        self.board = [[None for _ in range(width)] for _ in range(height)]
        self.figures_on_board = [[None for _ in range(width)] for _ in range(height)]
        self.cell_size = cell_size
        self.x = 0
        self.y = 0
        self.currect_bild = None
        self.currect_orientation = 0
        self.help = True

    def render(self, screen):
        viev_sprites = pygame.sprite.Group()
        viev_figures = []
        viev_belt = pygame.sprite.Group()
        for row in range(-self.y // self.cell_size - 2,
                         - self.y // self.cell_size + screen.get_height() // self.cell_size + 2):
            for col in range(-self.x // self.cell_size - 2,
                             - self.x // self.cell_size + screen.get_width() // self.cell_size + 2):
                if 0 <= row <= self.height and 0 <= col <= self.width:
                    pygame.draw.rect(screen, (165, 172, 188),
                                     (col * int(self.cell_size) + self.x, row * int(self.cell_size) + self.y,
                                      int(self.cell_size), int(self.cell_size)))
                    pygame.draw.rect(screen, (141, 148, 165),
                                     (col * int(self.cell_size) + self.x, row * int(self.cell_size) + self.y,
                                      int(self.cell_size), int(self.cell_size)), 1)
                    if 0 <= row < self.height and 0 <= col < self.width:
                        if self.board[row][col] is not None:
                            if self.board[row][col].__class__ is Belt or self.board[row][col].__class__ is BeltLeft or \
                                    self.board[row][col].__class__ is BeltRight:
                                viev_belt.add(self.board[row][col])
                            else:
                                viev_sprites.add(self.board[row][col])
                        if self.figures_on_board[row][col] is not None:
                            viev_figures.append(self.figures_on_board[row][col])
        viev_belt.update()
        viev_belt.draw(screen)
        for figure in viev_figures:
            figure.update_pos()
            figure.render()
        viev_sprites.update()
        viev_sprites.draw(screen)
        if self.currect_bild is not None:
            phantom_image = self.currect_bild.Sprite_images[self.cell_size][0][self.currect_orientation].copy()
            phantom_image.set_alpha(128)
            x, y = self.get_cell(pygame.mouse.get_pos())
            if self.currect_orientation % 2 == 0:
                size = self.currect_bild.Size
            else:
                size = (self.currect_bild.Size[1], self.currect_bild.Size[0])
            if any([self.board[y + j][x + i] is not None for i in range(size[0]) for j in range(size[1])]):
                red_filter(phantom_image)
                phantom_image.set_alpha(96)
            screen.blit(phantom_image, (self.get_cell(pygame.mouse.get_pos())[0] * self.cell_size + self.x,
                                        self.get_cell(pygame.mouse.get_pos())[1] * self.cell_size + self.y))
        if self.help:
            font = pygame.font.SysFont(None, 25)
            text = font.render(f"ЛКМ - Строить\nПКМ - Удалять\nКолесо мыши - Масштаб\nКлавиатура:\n1 - Belt\n2 - BeltLeft\n3 - BeltRight\n4 - Factory\n5 - Spliter\n6 - Connector\n7 - Deleter\n8 - Rotator\n9 - Painter\n0 - Asembler\nW, A, S, D - перемещение\nR - поворот\nQ - копировать постройку\nC - Показать/Скрыть подсказки", True, (0, 0, 0))
            screen.blit(text, (10, 100))

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.x) // self.cell_size
        cell_y = (mouse_pos[1] - self.y) // self.cell_size
        return (cell_x, cell_y)

    def build(self):
        if self.currect_bild is not None:
            x, y = self.get_cell(pygame.mouse.get_pos())
            if self.currect_orientation % 2 == 0:
                size = self.currect_bild.Size
            else:
                size = (self.currect_bild.Size[1], self.currect_bild.Size[0])
            if all([self.board[y + j][x + i] is None for i in range(size[0]) for j in range(size[1])]):
                self.currect_bild(self, *self.get_cell(pygame.mouse.get_pos()), self.currect_orientation)

    def delete(self):
        x, y = self.get_cell(pygame.mouse.get_pos())
        if self.board[y][x] is not None:
            self.board[y][x].kill()
            self.board[y][x] = None

    def change_current_bild(self, key):
        bildings_panel = {
            0: Asembler,
            1: Belt,
            2: BeltLeft,
            3: BeltRight,
            4: Factory,
            5: Spliter,
            6: Connector,
            7: Deleter,
            8: Rotator,
            9: Painting,
        }
        if self.currect_bild == bildings_panel[key]:
            self.currect_bild = None
        else:
            self.currect_bild = bildings_panel[key]

    def copy_to_current_bild(self):
        if self.currect_bild is None:
            x, y = self.get_cell(pygame.mouse.get_pos())
            if self.board[y][x] is not None:
                self.currect_bild = self.board[y][x].__class__
                self.currect_orientation = self.board[y][x].orientation
        else:
            self.currect_bild = None

    def update(self, *args):
        if args:
            event_type = args[0]
            if event_type == "resize":
                event = args[1]
                if event.button == 4 or event.button == 5:
                    step_resize = ZOOM_SPEED
                    k = step_resize / self.cell_size
                    if event.button == 4:
                        if self.cell_size < MAX_CELL_SIZE:
                            self.x = pygame.mouse.get_pos()[0] - abs(self.x - pygame.mouse.get_pos()[0]) * (1 + k)
                            self.y = pygame.mouse.get_pos()[1] - abs(self.y - pygame.mouse.get_pos()[1]) * (1 + k)
                            self.cell_size += step_resize
                    else:
                        if self.cell_size > MIN_CELL_SIZE:
                            self.x = pygame.mouse.get_pos()[0] - abs(self.x - pygame.mouse.get_pos()[0]) * (1 - k)
                            self.y = pygame.mouse.get_pos()[1] - abs(self.y - pygame.mouse.get_pos()[1]) * (1 - k)
                            self.cell_size -= step_resize
            elif event_type == "MouseButton_pressed":
                buttons = args[1]
                if buttons[0]:
                    self.build()
                if buttons[2]:
                    self.delete()
            elif event_type == "keydown":
                key = args[1].key
                bilds_keys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6,
                              pygame.K_7, pygame.K_8, pygame.K_9]
                if key == pygame.K_r:
                    self.currect_orientation = (self.currect_orientation + 1) % 4
                if key == pygame.K_l:
                    self.load()

                elif key == pygame.K_q:
                    self.copy_to_current_bild()

                elif key in bilds_keys:
                    self.change_current_bild(bilds_keys.index(key))

                elif key == pygame.K_c:
                    self.help = not self.help

        if pygame.key.get_pressed()[pygame.K_w]:
            self.y += MOVE_SPEED
        if pygame.key.get_pressed()[pygame.K_s]:
            self.y -= MOVE_SPEED
        if pygame.key.get_pressed()[pygame.K_a]:
            self.x += MOVE_SPEED
        if pygame.key.get_pressed()[pygame.K_d]:
            self.x -= MOVE_SPEED
        self.x = int(self.x) if self.x < 0 else 0
        self.y = int(self.y) if self.y < 0 else 0
        self.x = screen.get_width() - self.width * self.cell_size if self.x + self.width * self.cell_size < screen.get_width() else self.x
        self.y = screen.get_height() - self.height * self.cell_size if self.y + self.height * self.cell_size < screen.get_height() else self.y

    def in_viev(self, x, y):
        return (-2 * self.cell_size < self.x + x * self.cell_size < screen.get_width() + 2 * self.cell_size and
                -2 * self.cell_size < self.y + y * self.cell_size < screen.get_height() + 2 * self.cell_size)

    def save(self):
        with open("save_board.txt", "w") as f:
            code_board = [([None] * self.width) for _ in range(self.height)]
            for i in range(self.height):
                for j in range(self.width):
                    if self.board[i][j] is not None and self.board[i][j].__class__ in code_bildings:
                        code_board[i][j] = (code_bildings[self.board[i][j].__class__], self.board[i][j].orientation)
            f.write(str(code_board))

    def load(self):
        reverse_code_bildings = {v: k for k, v in code_bildings.items()}
        with open("save_board.txt", "r") as f:
            code_board = eval(f.read())
            for i in range(self.height):
                for j in range(self.width):
                    if code_board[i][j] is not None:
                        if self.board[i][j] is None:
                            reverse_code_bildings[code_board[i][j][0]](self, j, i, code_board[i][j][1])


class Interface:
    def __init__(self, width, height, cell_size=40):
        self.width = width
        self.height = height
        self.btn_width = int(width * 0.25)
        self.btn_height = int(height * 0.115)
        self.cell_size = cell_size
        self.ui_manager = pygame_gui.UIManager((width, height), "Data/theme.json")

        button_image = pygame.image.load("Data/Sprites/Button/menu_objects.png").convert_alpha()
        self.button_image = pygame.transform.scale(button_image, (
            self.btn_width // 8, self.btn_height // 2))  # Подгоните размер изображения под кнопку

        self.menu_actions_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((int(width - self.btn_width // 8), 0),
                                      (int(self.btn_width // 7), self.btn_height // 2)),
            text="",
            manager=self.ui_manager,
            object_id=pygame_gui.core.ObjectID(class_id="#main_button", object_id="#main_button")
        )

        # self.menu_objects_button = pygame_gui.elements.UIButton(
        #     relative_rect=pygame.Rect((width - int(self.btn_width // 1.5), height - self.btn_height),
        #                               (int(self.btn_width // 1.5), self.btn_height)),
        #     text="Постройки",
        #     manager=self.ui_manager,
        #     object_id=pygame_gui.core.ObjectID(class_id="#construction_button", object_id="#construction_button")
        # )

        self.menu_x = int(width - self.btn_width // 8) - int(self.btn_width // 3.75) - int(self.btn_width * 0.15)
        self.menu_y = 0
        self.menu_width = int(self.btn_width // 5)
        self.menu_expanded = False
        self.stop_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.menu_x, self.menu_y, self.menu_width,
                                      self.btn_height // 2),
            text="Стоп",
            manager=self.ui_manager,
            object_id=pygame_gui.core.ObjectID(class_id="#construction_button", object_id="#construction_button")
        )
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.menu_x + int(self.btn_width * 0.215), self.menu_y, self.menu_width,
                                      self.btn_height // 2),
            text="Выход",
            manager=self.ui_manager,
            object_id=pygame_gui.core.ObjectID(class_id="#construction_button", object_id="#construction_button")
        )

        self.clock = pygame.time.Clock()
        self.update_buttons_visibility()

    def toggle_menu(self):
        self.menu_expanded = not self.menu_expanded
        self.update_buttons_visibility()

    def update_buttons_visibility(self):
        if self.menu_expanded:
            self.exit_button.show()
            self.stop_button.show()
        else:
            self.exit_button.hide()
            self.stop_button.hide()

    def handle_button_click(self, button):
        if button == self.stop_button:
            return self.stop()
        elif button == self.exit_button:
            return False
        return True

    def stop(self):
        self.menu_actions_button.hide()
        self.menu_objects_button.hide()
        self.exit_button.hide()
        self.stop_button.hide()
        screen.fill((141, 148, 165))
        btn_width = int(self.width * 0.25)
        btn_height = int(self.height * 0.115)
        btn_x_center = self.width // 2 - btn_width // 2
        resume_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((int(btn_x_center), int(self.height * 0.3)), (btn_width, btn_height)),
            text="Продолжить",
            manager=self.ui_manager)
        exit2_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((int(btn_x_center), int(self.height * 0.45)), (btn_width, btn_height)),
            text="Завершить",
            manager=self.ui_manager)
        while True:
            time_delta = clock.tick(60) / 1000.0
            screen.fill((141, 148, 165))
            for event in pygame.event.get():
                self.ui_manager.process_events(event)
                if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == resume_button:
                    resume_button.hide()
                    exit2_button.hide()
                    self.menu_actions_button.show()
                    self.menu_objects_button.show()
                    return True
                if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == exit2_button:
                    resume_button.hide()
                    exit2_button.hide()
                    return False
            self.ui_manager.update(time_delta)
            self.ui_manager.draw_ui(screen)
            pygame.display.flip()

    def run(self, events, pos):
        for event in events:
            self.ui_manager.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.menu_actions_button:
                self.toggle_menu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_expanded:
                    if self.stop_button.rect.collidepoint(pos):
                        pygame.display.flip()
                        return self.handle_button_click(self.stop_button)
                    elif self.exit_button.rect.collidepoint(pos):
                        pygame.display.flip()
                        return self.handle_button_click(self.exit_button)
        pygame.display.flip()
        return True

    def update(self, time_delta):
        self.ui_manager.update(time_delta)

    def draw(self):
        self.ui_manager.draw_ui(screen)
        menu_actions_button_rect = self.menu_actions_button.relative_rect
        screen.blit(self.button_image, menu_actions_button_rect.topleft)


def init_game(new_game=False):
    global Board
    global data
    global render_count
    board = Board(101, 101, 40)
    interface = Interface(width, height)
    running = True
    fps = TICKS
    data = Data()
    board.x = -50 * board.cell_size + width // 2
    board.y = -50 * board.cell_size + height // 2
    if not new_game:
        board.load()
        data.load()
    else:
        Hub(board, 49, 49, 0)
    for bild in data.bildings_levels.keys():
        bild.Patern_delays[-1] = data.bildings_levels[bild][1][data.bildings_levels[bild][0]]

    # for i in range(5, 10):
    #     for j in range(5, 10):
    #         Belt(board, i, j, 1)
    # for i in range(5, 10):
    #     m = np.array([
    #         [(1, 0, 100, 200, 200), (1, 1, 100, 200, 200)],
    #         [(1, 3, 100, 200, 200), (1, 2, 100, 200, 200)]
    #     ])
    #     m = np.rot90(m, 3)
    #     for j in range(2):
    #         for k in range(2):
    #             m[j, k, 1] = (m[j, k, 1] - 3) % 4
    #     Figure(2, board, 5, i, m)

    while running:
        events = pygame.event.get()
        time_delta = clock.tick(fps) / 1000.0
        for event in events:
            if event.type == pygame.QUIT:
                board.save()
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
                board.update("resize", event)
            if event.type == pygame.KEYDOWN:
                board.update("keydown", event)
        running = interface.run(events, pygame.mouse.get_pos())
        if pygame.mouse.get_pressed():
            board.update("MouseButton_pressed", pygame.mouse.get_pressed())
        render_count = (render_count + 1) % 1
        if render_count == 0 or no_effectiveness_update:
            screen.fill((0, 0, 0))
            board.render(screen)
        if board.cell_size < 50:
            no_effectiveness_update = False
        else:
            no_effectiveness_update = True
        board.update()
        Belt.Update_animation()
        BeltRight.Update_animation()
        BeltLeft.Update_animation()
        # all_sprites.update()
        # all_sprites.draw(screen)
        cur_fps = clock.get_fps()
        fps_text = font.render(f'FPS: {int(cur_fps)}', True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))
        Factory.Update_animation()
        Spliter.Update_animation()
        BeltConnector.Update_animation()
        Connector.Update_animation()
        Rotator.Update_animation()
        Deleter.Update_animation()
        Painting.Update_animation()
        Asembler.Update_animation()
        Hub.Update_animation()
        Figure.Update()
        interface.update(time_delta)
        interface.draw()
        data.draw(screen)
        # pygame.draw.rect(screen, (128, 105, 102), (300, 300, 100, 100))
        # pygame.draw.rect(screen, (128, 105, 102), (300, 300, 100, 100))
        # pygame.draw.rect(screen, (55, 54, 59), (300, 300, 100, 100), 2)
        # screen.blit(pygame.image.load("Data/Sprites/Factory/Factory_1.png"), (200, 200))
        # pygame.draw.circle(screen, pygame.Color("#bec1c6"), (250, 250), 25)
        pygame.display.update()
    board.save()
    data.save()


if __name__ == '__main__':
    init_game()
    # Board = Board(500, 500, 40)
    # running = True
    # fps = TICKS
    # all_sprites = pygame.sprite.Group()
    # phantom_bilds = pygame.sprite.Group()
    #
    # for i in range(5, 10):
    #     for j in range(5, 10):
    #         Belt(Board, i, j, 1)
    # for i in range(5, 10):
    #     m = np.array([
    #         [(1, 0, 100, 200, 200), (2, 1, 100, 200, 200)],
    #         [(1, 3, 100, 200, 200), (1, 2, 100, 200, 200)]
    #     ])
    #     m = np.rot90(m, 3)
    #     for j in range(2):
    #         for k in range(2):
    #             m[j, k, 1] = (m[j, k, 1] - 3) % 4
    #     Figure(2, Board, 5, i, m)
    #
    # while running:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False
    #         if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
    #             Board.update("resize", event)
    #         if event.type == pygame.KEYDOWN:
    #             Board.update("keydown", event)
    #
    #     if pygame.mouse.get_pressed():
    #         Board.update("MouseButton_pressed", pygame.mouse.get_pressed())
    #     render_count = (render_count + 1) % 1
    #     if render_count == 0 or no_effectiveness_update:
    #         screen.fill((0, 0, 0))
    #         Board.render(screen)
    #     if Board.cell_size < 50:
    #         no_effectiveness_update = False
    #     else:
    #         no_effectiveness_update = True
    #     Board.update()
    #     Belt.Update_animation()
    #     # all_sprites.update()
    #     # all_sprites.draw(screen)
    #     clock.tick(fps)
    #     cur_fps = clock.get_fps()
    #     fps_text = font.render(f'FPS: {int(cur_fps)}', True, (255, 255, 255))
    #     screen.blit(fps_text, (10, 10))
    #     Figure.Update()
    #     Factory.Update_animation()
    #     # pygame.draw.rect(screen, (128, 105, 102), (300, 300, 100, 100))
    #     # pygame.draw.rect(screen, (55, 54, 59), (300, 300, 100, 100), 2)
    #     # screen.blit(pygame.image.load("Data/Sprites/Factory/Factory_1.png"), (200, 200))
    #     # pygame.draw.circle(screen, pygame.Color("#bec1c6"), (250, 250), 25)
    #     pygame.display.update()