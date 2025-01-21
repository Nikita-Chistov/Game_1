from turtledemo.penrose import start

import arcade
from arcade.gui import UILabel, UIFlatButton, UIManager
from pygame_gui.elements import UIButton
#from main import *
from settings import *
import pygame_gui


class MainMenuView(arcade.View):
    def __init__(self):
        super(MainMenuView, self).__init__()
        self.background = arcade.load_texture("Data/Sprites/Window/start_window1.png")
        self.ui_manager = UIManager(self.window)
        self.setup()

    def setup(self):
        start_button = arcade.gui.UIFlatButton(text="Начать игру",
                                    cepter_x=0.5,
                                    cepter_y=0.5,
                             color=(255, 255, 255),
                                    width=200)
        start_button.on_click = self.game
        self.ui_manager.add(start_button)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(self.window.width // 2, self.window.height // 2, self.background.width,
                                    self.background.height, self.background)
        arcade.draw_text(
            "Новогодняя фабрика",
            self.window.width // 2 + 100,
            self.window.width // 2 + 10,
            font_size=50,
            color=(255, 255, 255),
            font_name="Ink Free",
            anchor_x="center",
            anchor_y="center"
        )

    def game(self):
        pass



def main():
    window = arcade.Window(1920, 1080, "Cognetic")
    view = MainMenuView()
    window.show_view(view)
    arcade.run()

if __name__ == "__main__":
    main()
