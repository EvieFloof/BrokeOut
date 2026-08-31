"""
core.engine - Classe principale du moteur BrokeEngine
"""

import os

import pygame

from core import context, error_handler, event_manager, scene_manager
from systems import discord, logging, renderer
from systems.audio import AudioEngine
from systems.config import config

class Game:
    """
    Game - Classe principale du moteur
    """

    def __init__(self) -> None:
        self.config = config

        self.logger = logging.Logger("core.engine")

        self.logger.log(
            "Version " + " ".join([self.config.release[i] for i in self.config.release])
        )  # TODO: Make this more readable

        self.error_handler = (
            error_handler.ErrorHandler()
            if self.config.debug.misc.error_handler
            else None
        )

        context.GameContext.set_game(self)

        self.scene_manager = scene_manager.SceneManager()
        self.event_manager = event_manager.EventManager()
        self.audio_engine = AudioEngine()

        self.discordrpc = discord.DiscordRPC()

        self.running = True

        self.isFullscreen = False

        self.fixed_dt = 1.0 / self.config.graphics.tps
    
    def change_fixed_dt(self, dt):
        self.fixed_dt = 1.0 / dt

    def handle_events(self) -> bool:
        """
        handle_event - Envoyer les évènements au gestionnaire d'évènements
        """

        return self.event_manager.handle_events()

    def update_window_title(self, text="") -> str:
        """
        update_window_title - modifier le nom de la fenêtre en utilisant le format fixe
        """

        new_title: str = (
            "BrokeOut"
            + f" {self.config.release.version} ({self.config.release.state}) : {self.config.release.compliant_name}"
            + (" - " if text != "" else "")
            + text
        )
        pygame.display.set_caption(new_title)
        return new_title

    def update(self) -> None:
        """
        update - Connecteur de la fonction update du scene_manager
        """

        self.scene_manager.update()

    def draw(self) -> None:
        """
        draw - Connecteur de la fonction draw du scene_manager
        """

        self.scene_manager.draw()

    def set_pygame_window_mode(self, fullscreen: bool = False) -> None:
        if fullscreen:
            self.window = pygame.display.set_mode(
                (self.config.graphics.window.width, self.config.graphics.window.height),
                pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN,
            )
        else:
            self.window = pygame.display.set_mode(
                (self.config.graphics.window.width, self.config.graphics.window.height),
                pygame.OPENGL | pygame.DOUBLEBUF,
            )

    def run(self) -> int:
        """
        run - Fonction d'exécution du moteur de jeu
        """

        self.logger.log(f"Current platform : {os.name}")

        self.logger.log("Initialising Pygame window")
        pygame.init()
        self.audio_engine.start()

        self.set_pygame_window_mode(self.isFullscreen)

        self.update_window_title()

        pygame.mouse.set_visible(False)

        self.renderer = renderer.Renderer()

        self.clock = pygame.time.Clock()
        self._accumulator = 0.0

        if self.config.debug.startup.scene != "default":
            self.active_scene = self.scene_manager.set_active_scene(
                self.config.debug.startup.scene
            )
        else:
            self.active_scene = self.scene_manager.set_active_scene("splash")

        self.logger.success("Changed current active scene")

        while self.running:
            frame_time = self.clock.tick(self.config.graphics.fps) / 1000.0
            frame_time = min(frame_time, 0.25)

            self.handle_events()

            self._accumulator += frame_time
            while self._accumulator >= self.fixed_dt:
                self.update()
                self._accumulator -= self.fixed_dt

            self.draw()
            pygame.display.flip()

        self.audio_engine.stop()
        pygame.quit()
        return 0
