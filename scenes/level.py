import random

import numpy as np
import pygame
import pygame.freetype

from assets.levels.levels import levels
from core.scene_manager import Scene
from effects import screen_shake
from effects.gaussian_blur import gaussian_blur
from objects.gui import button, hint, mouse
from objects.level import ball, brick, player
from objects.level.stats import ProgressBar, StatsElement
from objects.menu import logo


class LevelScene(Scene):
    def __init__(self) -> None:
        super().__init__()

        self.game_started: bool = False
        self.lives: int = (
            self.game.config.game.initial_lives
            if not self.game.config.debug.game.infinite_lives
            else -1
        )
        self.level: int = 1
        self.score: int = 0

        self.levels: list[list] = levels
        self.level_size = np.count_nonzero(
            self.levels[(self.level - 1) % len(self.levels)]
        )

        self.color: list[int] = [255, 153, 191]

        self.font = pygame.freetype.Font("assets/fonts/Monocraft.ttf", 36)

        self.bounds: dict = {
            "x_min": 0,
            "y_min": 0,
            "x_max": self.game.config.graphics.render.width,
            "y_max": self.game.config.graphics.render.height,
        }

        self.screen_shake = screen_shake.ScreenShake()
        self.offset: list[int] = [0, 0]

        self.blur_radius: int = 0

        self.game.audio_engine.load_sound("level_theme_0", "music/audio0_extended.wav")

        self.backspeed = 4

        self.renderer = self.game.renderer

    def run(self) -> None:
        self.pause: bool = False
        self.renderer.update_values = True

        self.game.update_window_title("Classic Game")

        self.game.event_manager.subscribe(self, "MouseButtonDown")
        self.game.event_manager.subscribe(self, "KeyDown")

        self.player = player.Player()
        self.ball = ball.Ball()

        self.brick_group = brick.BrickGroup()
        self.skeleton = brick.BricksSkeleton()
        self.brick_group.generate_bricks()

        self.stats = [StatsElement(), ProgressBar(), hint.HintElement()]

        self.logo = logo.LogoElement()

        pygame.mouse.set_visible(False)

        if self.game.config.debug.game.autostart:
            self.ball.on_player = False
            self.ball.set_velocity_by_angle(60)
            self.game_started = True

        self.LoseMessages: list[str] = [
            "Oopsie :3",
            "Maybe do better next time",
            "Actually that was fun",
            "Ew you don't play very well",
            "You have to touch the ball actually",
            "Stop being bad, it makes me sad",
            "-3/10",
            "Lives are falling like this ball",
            "Try harder :P",
            "nothing beats a jet2 holiday",
            "keep them coming",
            "...",
        ]

        center: tuple[int, int] = self.game.window.get_rect().center

        self.pause_buttons: dict[str, button.Button] = {
            "Resume": button.Button(
                (center[0], center[1]),
                [305, 51],
                "Resume",
                self.toggle_pause,
            ),
            "Settings": button.Button(
                (center[0] - 77, center[1] + 53), [151, 51], "Settings", disabled=True
            ),
            "Quit Game": button.Button(
                (center[0] + 77, center[1] + 53),
                [151, 51],
                "Main Menu",
                self.MenuButton,
            ),
            "Quit Desktop": button.Button(
                (center[0], center[1] + 106),
                [305, 51],
                "Exit the game",
                lambda: self.game.__setattr__("running", False),
            ),
        }

        for button_element in self.pause_buttons:
            self.pause_buttons[button_element].set_event_state(False)

        self.game.discordrpc.set_rich_presence(
            "Playing in classic mode", f"Level {self.level}"
        )

        self.game.audio_engine.play_sound("level_theme_0", True)

    def MenuButton(self) -> None:
        self.game.audio_engine.set_lowpass(50_000)
        self.game.scene_manager.set_active_scene("menu")

    def background_color(self) -> list:
        return [c // 3 for c in self.color]

    def render_background(self, surface: pygame.Surface) -> None:
        background = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA, 32)
        for line in range(self.game.config.graphics.render.height // 45):
            for column in range(self.game.config.graphics.render.width // 45):
                pygame.draw.rect(
                    background,
                    (0, 0, 0, 25),
                    (
                        -25 + (column * 51),
                        -40 + (line * 51) + (self._get_ticks() // self.backspeed) % 50,
                        45,
                        45,
                    ),
                )
        surface.blit(background, (0, 0))

    def reset_game(self) -> None:
        self.screen_shake.start(10, 5)

        self.brick_group.generate_bricks()

        self.color = [255, 153, 191]
        self.game_started = False
        self.level = 1
        self.lives = self.game.config.game.initial_lives
        self.score = 0

        self.ball.speed = self.game.config.game.ball.speed
        self.player.width = self.player.base_width

        self.stats[2].show_hint(f"Level {self.level}", size=24)
        self.game.discordrpc.set_rich_presence(
            "Playing in classic mode", f"Level {self.level}"
        )

    def trigger_next_level(self) -> None:
        self.level += 1

        self.color = [random.randint(150, 255) for _ in range(3)]
        self.skeleton = brick.BricksSkeleton()
        self.brick_group.generate_bricks()

        self.screen_shake.start(10, 5)
        self.level_size = np.count_nonzero(
            self.levels[(self.level - 1) % len(self.levels)]
        )
        self.lives += 4

        self.logger.log(f"{self.level_size=}")

        self.stats[2].show_hint(f"Level {self.level}", size=24)
        self.game.discordrpc.set_rich_presence(
            "Playing in classic mode", f"Level {self.level}"
        )

    def trigger_lose(self) -> None:
        if self.lives != 1:
            self.stats[2].show_hint(random.choice(self.LoseMessages), size=24)
            self.lives -= 1
            self.logger.log(
                f"Player lose this round, now having {self.lives} more lives"
            )
        else:
            self.logger.log("Player lose the game, resetting all states")
            self.reset_game()
        self.ball.on_player = True

    def toggle_pause(self):
        self.blur_radius = 0
        self.pause = not self.pause
        self.game.audio_engine.fade_lowpass(250 if self.pause else 50_000, 0.5)
        for button_element in self.pause_buttons:
            self.pause_buttons[button_element].set_event_state(self.pause)
        self.renderer.update_values = not self.renderer.update_values
        self.renderer.set_curvature(0)

    def MouseButtonDown(self, event: pygame.Event) -> None:
        if event.button == 1 and self.ball.on_player and not self.pause:
            self.ball.on_player = False
            self.ball.set_velocity_by_angle(60)

            if not self.game_started:
                self.level = 1
                self.game_started = True

    def KeyDown(self, event: pygame.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            if self.game.config.debug.game.exit_on_escape:
                self.game.running = False
            self.toggle_pause()
        if event.key == pygame.K_SPACE:
            self.trigger_next_level()

    def compute_surface_offset(self) -> None:
        if pygame.mouse.get_focused():
            self.mousex, self.mousey = pygame.mouse.get_pos()
        else:
            center_x, center_y = self.game.window.get_rect().center
            self.mousex += (center_x - self.mousex) * 0.1
            self.mousey += (center_y - self.mousey) * 0.1

    def update(self) -> None:
        # self.color = [random.randint(150,255) for i in range(3)]

        if self.blur_radius < 10 and self.pause:
            self.blur_radius += (10 - self.blur_radius) * 0.3

        if not self.pause:
            [i.update() for i in self.stats]
            self.brick_group.update()
            self.player.update()
            self.ball.update()
        else:
            for i in self.pause_buttons:
                self.pause_buttons[i].update()
            self.logo.update()

    def draw(self) -> None:
        self.offset = self.screen_shake.get_offset()

        self.game.window.fill([c // 3 for c in self.color])

        self.surface = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA)

        self.render_background(self.surface)


        self.skeleton.draw()
        self.brick_group.draw()
        self.player.draw()
        self.ball.draw()

        [element.draw() for element in self.stats]
        
        if not self.pause:
            self.game.window.blit(self.surface, self.offset)

        if self.pause:
            self.compute_surface_offset()

            pause_surface = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA)

            self.game.window.blit(self.surface, (1 + ((self.mousex - 400) // 50),
                1 + ((self.mousey - 300) // 50)))

            self.game.window = gaussian_blur(self.game.window, self.blur_radius)

            self.logo.draw(pause_surface)

            # Menu pause code
            for i in self.pause_buttons:
                self.pause_buttons[i].draw(pause_surface, [c // 2 for c in self.color], self.color)

            self.game.window.blit(pause_surface,
            (1 + ((self.mousex - 400) // 30),
                1 + ((self.mousey - 300) // 30)))

            mouse.Mouse().draw()


        self.renderer.render_frame()
