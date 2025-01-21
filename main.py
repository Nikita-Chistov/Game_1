from settings import *
import numpy as np
import pygame
import os
import sys
import random
from PIL import Image

pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
pygame.display.set_caption('RTKY')
size = width, height = 500, 500
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
font = pygame.font.SysFont(None, 30)


def get_resize_images(name):
    images = {}
    for size in range(MIN_CELL_SIZE - ZOOM_SPEED, MAX_CELL_SIZE + ZOOM_SPEED, ZOOM_SPEED):
        size_images = []
        for root, _, files in os.walk(os.path.join("Data", "Sprites", name)):
            sort_files = sorted(files, key=lambda x: int(x.split('.')[0].split('_')[-1]))
            for image_name in sort_files:
                image_path = os.path.join(root, image_name)
                image = load_image(image_path)
                pil_image = Image.frombytes('RGBA', image.get_size(), pygame.image.tostring(image, 'RGBA'))
                resized_image = pil_image.resize((size, size), Image.LANCZOS)
                resized_surface = pygame.image.fromstring(resized_image.tobytes(), resized_image.size, 'RGBA')
                resized_surface = resized_surface.convert_alpha()
                size_images.append(resized_surface)
                print(image_name)
        images[size] = size_images
    return images


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


class Bildings(pygame.sprite.Sprite):
    Sprite_images = get_resize_images("conv")
    Size = (1, 1)
    Patern_delays = [60]
    Patern_images = [0]
    capture = 0
    current_sprite = 0
    Sprite_group = pygame.sprite.Group()

    def check_have_figure(self):
        if self.board.figures_on_board[self.y][self.x] != None:
            return True
        return False

    @classmethod
    def Update_animation(cls):
        print(cls.current_sprite, cls.capture)
        cls.capture = (cls.capture + 1) % cls.Patern_delays[-1]
        if cls.capture in cls.Patern_delays:
            cls.current_sprite = cls.Patern_images[cls.Patern_delays.index(cls.capture)]
        if cls.capture == cls.Patern_delays[-1]:
            for sprite in cls.Sprite_group:
                sprite.have_figure = sprite.check_have_figure()
                if sprite.have_figure:
                    sprite.create_product()

    def create_product(self):
        pass

    def __init__(self, group, board, x, y):
        super().__init__(group)
        self.__class__.Sprite_group.add(self)
        self.size = self.Size
        self.x = x
        self.y = y
        board.board[self.y][self.x] = self
        self.board = board
        self.rect = pygame.Rect(0, 0, self.Size[0] * self.board.cell_size, self.Size[1] * self.board.cell_size)
        self.update_image()
        self.have_figure = False

    def update_image(self):
        self.image = self.Sprite_images[self.board.cell_size][self.current_sprite]

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


class Conv(Bildings):
    Sprite_images = get_resize_images("Belt")
    Size = (1, 1)
    Patern_delays = list(range(0, 100, 1))
    Patern_images = list(range(0, 100, 1))
    #Patern_delays = [30, 40, 50]
    #Patern_images = [10, 40, 90]
    capture = 0
    current_sprite = 0


class Board:
    def __init__(self, width, height, cell_size=20):
        self.width = width
        self.height = height
        self.board = [[None for _ in range(width)] for _ in range(height)]
        self.figures_on_board = [[None for _ in range(width)] for _ in range(height)]
        self.cell_size = cell_size
        self.x = 0
        self.y = 0
        self.currect_bild = Conv

    def render(self, screen):
        viev_sprites = pygame.sprite.Group()
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
                    if self.board[row][col] is not None:
                        viev_sprites.add(self.board[row][col])
        viev_sprites.update()
        viev_sprites.draw(screen)

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.x) // self.cell_size
        cell_y = (mouse_pos[1] - self.y) // self.cell_size
        return (cell_x, cell_y)

    def build(self):
        if self.currect_bild is not None:
            x, y = self.get_cell(pygame.mouse.get_pos())
            if self.board[y][x] is None:
                self.board[y][x] = self.currect_bild(all_sprites, self, *self.get_cell(pygame.mouse.get_pos()))

    def delete(self):
        x, y = self.get_cell(pygame.mouse.get_pos())
        if self.board[y][x] is not None:
            self.board[y][x].kill()
            self.board[y][x] = None

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
            if event_type == "MouseButton_pressed":
                buttons = args[1]
                if buttons[0]:
                    self.build()
                if buttons[2]:
                    self.delete()

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


if __name__ == '__main__':
    Board = Board(500, 500, 40)
    running = True
    fps = TICKS
    all_sprites = pygame.sprite.Group()

    for i in range(100):
        for j in range(100):
            Conv(all_sprites, Board, i, j)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
                Board.update("resize", event)

        if pygame.mouse.get_pressed():
            Board.update("MouseButton_pressed", pygame.mouse.get_pressed())

        screen.fill((0, 0, 0))
        Board.update()
        Board.render(screen)
        Conv.Update_animation()
        # all_sprites.update()
        # all_sprites.draw(screen)
        clock.tick(10)
        cur_fps = clock.get_fps()
        fps_text = font.render(f'FPS: {int(cur_fps)}', True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))
        pygame.display.update()
