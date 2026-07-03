# type: ignore

import random
import webbrowser

import pygame

from core.scene_manager import Scene
from effects import screen_shake
from objects.gui import mouse, button, hint
from objects.menu import credits
from systems import renderer, logging


class MenuScene(Scene):
    def __init__(self) -> None:
        super().__init__()

        self.logger: logging.Logger = logging.Logger("scenes.menu")
        self.color: list[int] = [246, 172, 201]

        self.font = pygame.freetype.Font("assets/fonts/Monocraft.ttf", 36)
        self.text: str = "Broke Out"

        self.shake = screen_shake.ScreenShake()

        self.titley: int = self.game.config.graphics.render.height // 2
        self.titlesize: int = 36

        self.credits: bool = False

        self.game.audio_engine.load_sound("menu_theme", "music/audio_menu.wav")

    def run(self) -> None:
        self.game.update_window_title("Main Menu")

        self.game.event_manager.subscribe(self, "KeyDown")

        self.shaders = renderer.Renderer("crt")

        self.mouse = mouse.Mouse()

        self.shake.start(15, 5)

        self.hint = hint.HintElement()

        self.credits_object = credits.Credits()

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
            "Web": button.Button(
                (center[0] + 79, center[1] + 59),
                [151, 51],
                "Website",
                self.WebsiteButtonClick,
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

        self.gradient = pygame.image.load(
            "assets/images/store/gradient0.png"
        ).convert_alpha()
        self.gradient_rect: tuple = self.gradient.get_rect()

        self.game.audio_engine.play_sound("menu_theme", True)

    def Quit(self) -> None:
        self.game.running = False

    def render_background(self, shake: list[int]) -> None:
        background = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA, 32)
        for line in range(17):
            for column in range(19):
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
                1 + ((self.mousex - 400) // 25) + shake[0],
                1 + ((self.mousey - 300) // 20) + shake[1],
            ),
        )
        self.game.window.blit(
            background,
            (
                1 + ((self.mousex - 400) // 20) + shake[0],
                1 + ((self.mousey - 300) // 20) + shake[1],
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

    def WebsiteButtonClick(self) -> None:
        self.logger.log("Opening website in user's default browser")
        webbrowser.open("https://nowewo.github.io/BrokeOut/")

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
            self.shaders.set_curvature(0.4)

        if self.text_rect is not None:
            if self.text_rect.center[1] > 100:
                self.titley += (100 - self.titley) * 0.1

        if self.titlesize < 50:
            self.titlesize += (51 - self.titlesize) * 0.1

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

            self.text_rect = self.font.get_rect(f"Version {version} • {name}", size=19)

            self.text_rect.center = (
                self.surface.get_rect().center[0],
                self.titley + 51,
            )
            self.font.render_to(
                self.surface,
                self.text_rect,
                f"Version {version} • {name}",
                (206, 114, 150),
                size=19,
            )
        else:
            # Credits surface
            self.credits_object.draw(self)
            pygame.draw.rect(
                self.surface,
                (bg[0], bg[1], bg[2], 1),
                (0, 0, self.game.config.graphics.render.width, 131),
            )

        # Title element ("Broke Out")
        self.text_rect = self.font.get_rect(self.text, size=self.titlesize)

        self.text_rect.center = (self.surface.get_rect().center[0], self.titley + 5)
        self.font.render_to(
            self.surface, self.text_rect, self.text, (173, 95, 125), size=self.titlesize
        )

        self.text_rect.center = (self.surface.get_rect().center[0], self.titley)
        self.font.render_to(
            self.surface, self.text_rect, self.text, self.color, size=self.titlesize
        )

        self.hint.draw()

        self.render_background(shake)

        self.game.window.blit(self.gradient, (0, 0))

        self.game.window.blit(
            self.surface,
            (
                1 + ((self.mousex - 400) // 10) + shake[0],
                1 + ((self.mousey - 300) // 10) + shake[1],
            ),
        )

        self.mouse.draw()

        self.shaders.render_frame()
