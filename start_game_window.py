import pygame
import pygame_gui
from main import *


class MainMenu:
    def __init__(self):
        pygame.init()
        self.window_size = (1920, 1080)
        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        pygame.display.set_caption("Новогодняя фабрика")
        background = pygame.image.load("Data/Sprites/Window/start_window1.png").convert()
        self.background = pygame.transform.smoothscale(background, self.screen.get_size())
        self.screen.blit(self.background, (0, 0))

        self.ui_manager = pygame_gui.UIManager(self.window_size, "Data/theme.json")

        self.restart_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((850, 300), (350, 100)),
            text="Начать игру",
            manager=self.ui_manager
        )

        self.start_game_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((850, 400), (350, 100)),
            text="Продолжить игру",
            manager=self.ui_manager
        )

        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((1350, 780), (200, 100)),
            text="Выход",
            manager=self.ui_manager,
            object_id = pygame_gui.core.ObjectID(class_id='#exit_button',
                object_id='#exit_button'))

        self.clock = pygame.time.Clock()
        self.running = True

        pygame.mixer.init()
        self.music = pygame.mixer.Sound("Data/misic/christmas-tree-with-ornaments-shaking-looping_zkftfhv_.wav")

    def run(self):
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            font = pygame.font.SysFont("Ink Free", 70)
            title_surface = font.render("Новогодняя фабрика", True, (255, 255, 255))
            title_rect = title_surface.get_rect(center=(self.window_size[0] // 2 + 80, 200))
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(title_surface, title_rect)

            for event in pygame.event.get():
                if event.type== pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.restart_button:
                            self.restart_game()
                        if event.ui_element == self.start_game_btn:
                            self.start_game()
                        if event.ui_element == self.exit_button:
                            self.running = False
                self.ui_manager.process_events(event)
            self.ui_manager.update(time_delta)
            self.ui_manager.draw_ui(self.screen)

            pygame.display.flip()

        pygame.quit()

    def start_game(self):
        print("Продолжение игры.")
        self.music.play(loops=-1)

    def restart_game(self):
        print("Новая игра началась!")
        self.music.play(loops=-1)
        init_game()

    def exit_game(self):
        print("Выход из игры.")


if __name__ == "__main__":
    main_menu = MainMenu()
    main_menu.run()
