# type: ignore

import pygame
import pygame.freetype

from core.scene_manager import Scene
from systems import renderer


class SplashScene(Scene):
    # noinspection PyDefaultArgument
    def __init__(self) -> None:
        super().__init__()
        self.color: list[int] = [0, 0, 0]

        self.renderer = self.game.renderer

        self.fadeout: int = 0
        self.text_opacity: int = 0

        self.font = pygame.freetype.Font("assets/fonts/Monocraft.ttf", 36)
        self.text: str = "Made with love by Broke Team"
        self.text_color: list[int] = [255, 255, 255]
        self.animation_state: bool = False

        self.song_played: bool = False

        self.game.audio_engine.load_sound("splash_sound", "sfx/splash.wav")

    def run(self) -> None:
        self.game.event_manager.subscribe(self, "KeyDown")
        (self
        .at(60, lambda: self.register_update(self._intro_sequence))
        .at(60, lambda: setattr(self, "animation_state", True))
        .at(120, lambda: self.remove_update(self._intro_sequence))
        .at(120, lambda: setattr(self, "text", "Powered by BrokeEngine"))
        .at(180, lambda: setattr(self, "text", "© 2025-2026"))
        .at(230, lambda: self.register_update(self._outro_sequence))
        .at(270, lambda: self.game.scene_manager.set_active_scene("menu"))
        )
    
    def _intro_sequence(self):
        self.text_opacity += (255 - self.text_opacity) * 0.1
        if not self.song_played:
            self.text = "Made with love by Broke Team"
            self.song_played = True
            self.game.audio_engine.play_sound("splash_sound")

    def _outro_sequence(self):
        self.fadeout += (255 - self.fadeout) * 0.03
        self.text_color = [255, 153, 191]
        indice = (self._get_ticks() - 230) // 4
        self.text = "Broke Out"[0 : int(indice)]

    def KeyDown(self, event: pygame.Event) -> None:
        if event.key == pygame.K_SPACE:
            self.game.scene_manager.set_active_scene("menu")

    def draw(self) -> None:
        self.game.window.fill(self.color)

        surface = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA)

        overlay = pygame.Rect(
            0,
            0,
            self.game.config.graphics.render.width,
            self.game.config.graphics.render.height,
        )
        pygame.draw.rect(
            surface, (255 // 3, 153 // 3, 191 // 3, self.fadeout), overlay, 0
        )

        text_rect = self.font.get_rect(self.text, size=36)
        text_rect.center = surface.get_rect().center

        self.font.render_to(
            surface,
            text_rect,
            self.text,
            (
                self.text_color[0],
                self.text_color[1],
                self.text_color[2],
                self.text_opacity,
            ),
            size=36,
        )

        if self.game.config.release.state == "EDGE":
            rect = self.font.get_rect("UNSTABLE RELEASE", size=15)
            rect.center = surface.get_rect().center
            rect.centery = self.game.config.graphics.render.height - 51
            self.font.render_to(
                surface,
                rect,
                "UNSTABLE RELEASE",
                (231, 219, 125),
                size=15,
            )

        self.game.window.blit(surface, (0, 0))

        self.renderer.render_frame()
