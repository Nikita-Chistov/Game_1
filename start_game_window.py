import pygame
import pygame_gui
from main import *


class MainMenu:
    def __init__(self):
        pygame.init()
        display_info = pygame.display.Info()
        self.window_size = (display_info.current_w, display_info.current_h)
        self.screen = pygame.display.set_mode(self.window_size, pygame.FULLSCREEN)
        pygame.display.set_caption("Новогодняя фабрика")
        background = pygame.image.load("Data/Sprites/Window/start_window1.png").convert()
        self.background = pygame.transform.smoothscale(background, self.window_size)
        self.screen.blit(self.background, (0, 0))

        self.ui_manager = pygame_gui.UIManager(self.window_size, "Data/theme.json")

        btn_width = int(self.window_size[0] * 0.25)
        btn_height = int(self.window_size[1] * 0.115)
        btn_x_center = self.window_size[0] // 2 - btn_width // 2

        self.restart_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((int(btn_x_center*1.45), int(self.window_size[1] * 0.35)), (btn_width, btn_height)),
            text="Начать игру",
            manager=self.ui_manager
        )

        self.start_game_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((int(btn_x_center*1.45), int(self.window_size[1] * 0.45)), (btn_width, btn_height)),
            text="Продолжить игру",
            manager=self.ui_manager
        )

        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.window_size[0] - btn_width, self.window_size[1] - btn_height),
                                      (btn_width, btn_height)),
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
            font = pygame.font.SysFont("Ink Free", int(self.window_size[1] * 0.1))
            title_surface = font.render("Новогодняя фабрика", True, (255, 255, 255))
            title_rect = title_surface.get_rect(center=(int(self.window_size[0] // 1.5), int(self.window_size[1] * 0.25)))
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
