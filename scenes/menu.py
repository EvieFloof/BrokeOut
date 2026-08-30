# type: ignore

import random
import webbrowser

import pygame

from core.scene_manager import Scene
from effects import screen_shake
from objects.gui import button, hint, mouse
from objects.menu import credits, logo
from systems import logging, renderer


class MenuScene(Scene):
    def __init__(self) -> None:
        super().__init__()

        self.logger: logging.Logger = logging.Logger("scenes.menu")
        self.color: list[int] = [246, 172, 201]

        self.font = pygame.freetype.Font("assets/fonts/Monocraft.ttf", 36)

        self.shake = screen_shake.ScreenShake()

        self.credits: bool = False

        self.game.audio_engine.load_sound("menu_theme", "music/audio_menu.wav")

        self.renderer = self.game.renderer
        self.renderer.change_shader("crt")

    def run(self) -> None:
        self.game.update_window_title("Main Menu")

        self.game.event_manager.subscribe(self, "KeyDown")

        self.mouse = mouse.Mouse()

        self.shake.start(15, 5)

        self.hint = hint.HintElement()

        self.credits_object = credits.Credits()

        self.Logo = logo.LogoElement()

        center: tuple[int] = self.game.window.get_rect().center

        self.menu_buttons: dict[str, button.Button] = {
            "Play": button.Button(
                (center[0], center[1]), [193, 51], "Play", self.PlayButtonClick
            ),
            "Credits": button.Button(
                (center[0] - 79, center[1] + 59),
                [151, 51],
                "Credits",
                self.CreditsButtonClick,
            ),
            "Mods": button.Button(
                (center[0] + 79, center[1] + 59),
                [151, 51],
                "Mods",
                None,
            ),
            "Quit": button.Button(
                (center[0], center[1] + 118), [193, 51], "Quit", self.Quit
            ),
        }

        self.mousex, self.mousey = 400, 300
        self.scroll: int = 0

        self.hint_opacity: int = 255

        self.text_rect: bool = None
        self.egg: bool = False

        self.game.discordrpc.set_rich_presence(
            "Navigating in menus",
            f"Breakout Version {self.game.config.release.version}",
        )
        self.hint.show_hint("Connected to Discord", 120, 15)

        self.game.audio_engine.play_sound("menu_theme", True)


    def Quit(self) -> None:
        self.game.running = False

    def render_background(self, shake: list[int]) -> None:
        background = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA, 32)
        for line in range(self.game.config.graphics.render.height // 45):
            for column in range(self.game.config.graphics.render.width // 45):
                pygame.draw.rect(
                    background,
                    (0, 0, 0, 25),
                    (
                        -25 + (column * 51),
                        -40 + (line * 51) - (self._get_ticks() // 4) % 50,
                        45,
                        45,
                    ),
                )

        self.game.window.blit(
            background,
            (
                1
                + ((self.mousex - (self.game.config.graphics.render.width // 2)) // 25)
                + shake[0],
                1
                + ((self.mousey - (self.game.config.graphics.render.height // 2)) // 20)
                + shake[1],
            ),
        )
        self.game.window.blit(
            background,
            (
                1
                + ((self.mousex - (self.game.config.graphics.render.width // 2)) // 20)
                + shake[0],
                1
                + ((self.mousey - (self.game.config.graphics.render.height // 2)) // 20)
                + shake[1],
            ),
        )

    def PlayButtonClick(self) -> None:
        if not self.credits:
            self.game.scene_manager.set_active_scene("level", False)

    def CreditsButtonClick(self) -> None:
        self.scroll = 0
        self.egg = random.randint(0, 10) == 5 or self.game.config.debug.misc.easter_egg
        self.logger.log(f"Switching to credits with easter egg = {self.egg}")
        self.credits = True

    def KeyDown(self, event: pygame.Event) -> None:
        if event.key == pygame.K_ESCAPE and self.credits:
            self.logger.log("Disabling credits")
            self.credits = False
        if event.key == pygame.K_SPACE:
            self.game.scene_manager.set_active_scene("menu", False)

    def compute_surface_offset(self) -> None:
        if pygame.mouse.get_focused():
            self.mousex, self.mousey = pygame.mouse.get_pos()
        else:
            center_x, center_y = self.game.window.get_rect().center
            self.mousex += (center_x - self.mousex) * 0.1
            self.mousey += (center_y - self.mousey) * 0.1

    def update(self) -> None:
        if self._get_ticks() % 26 == 0 and self.game.config.debug.shaders:
            self.renderer.set_curvature(0.4)

        self.Logo.update()

        if self.game.config.debug.offset:
            self.compute_surface_offset()

        self.credits_object.update()
        self.hint.update()

    def draw(self) -> None:
        version, name = (
            self.game.config.release.version,
            self.game.config.release.compliant_name,
        )

        shake = self.shake.get_offset()

        bg = [145, 81, 106]  # [c // 3 for c in self.color]
        self.game.window.fill(bg)

        self.surface = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA, 32)

        if not self.credits:
            # Display main menu
            [
                self.menu_buttons[element].draw(self.surface, self.color)
                for element in self.menu_buttons
            ]

        else:
            # Credits surface
            self.credits_object.draw(self)
            pygame.draw.rect(
                self.surface,
                (bg[0], bg[1], bg[2], 1),
                (0, 0, self.game.config.graphics.render.width, 131),
            )

        # Logo
        self.Logo.draw(self.surface)

        self.hint.draw()

        self.render_background(shake)

        self.game.window.blit(
            self.surface,
            (
                1 + ((self.mousex - 400) // 10) + shake[0],
                1 + ((self.mousey - 300) // 10) + shake[1],
            ),
        )

        self.mouse.draw()

        self.renderer.render_frame()
