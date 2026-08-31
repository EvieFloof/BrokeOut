"""
core.scene_manager - Gestion de l'affichage des scènes et des entitées

Contenu:

Classe SceneManager
Classe Scene

EwoFluffy - BrokeTeam - 2026
"""

import importlib
import sys

from collections import defaultdict
from typing import Callable, Self

import pygame

from core import context
from systems import logging, renderer

def _scene_class_name(scene_name: str) -> str:
    """'scenes.main_menu' -> 'MainMenuScene'"""
    last_segment = scene_name.split(".")[-1]
    return "".join(part.capitalize() for part in last_segment.split("_")) + "Scene"

class Scene(context.Context):
    """
    Scene - Écran du jeu pouvant contenir des entitées
    """

    def __init__(self) -> None:
        self.logger = logging.Logger("core.scene_manager.scene")
        self.runtime_timer = 0.0
        self.actions: dict[int, list[Callable[[], None]]] = defaultdict(list)
        super().__init__()
        self.logger.success(f"New scene loaded as {self}")
        self.update_elements = []
    
    def at(self, time: int, action: Callable[[], None]) -> Self:
        self.actions[time].append(action)
        self.logger.success(f"Registered new action {action.__name__} to run at tick {time}", "action_manager")
        return self

    def after(self, time: int, action: Callable[[], None]) -> Self:
        self.actions[self.runtime_timer + time].append(action)
        self.logger.success(f"Registered new delayed action {action.__name__} to run at tick {self.runtime_timer + time} ({time} tick after current tick)", "action_manager")
        return self
    
    def register_update(self, action):
        self.update_elements.append(action)
        return self.update_elements[-1]
        self.logger.success(f"Registered new update function {action.__name__}", "update_manager")
    
    def remove_update(self, action):
        self.update_elements.remove(action)
        self.logger.success(f"Unregistered update function {action.__name__}", "update_manager")
        del action

    def run(self) -> None:
        """
        run - Fonction executée lorsque la scène devient active
        """

        self.logger.log(f"Scene {self} now running")

    def inactive(self) -> None:
        """
        inactive - Fonction executée lorsque la scène va devenir inactive
        """

        self.logger.log(f"Scene {self} now inactive")
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self.runtime_timer = 0

    def _get_ticks(self) -> float:
        """
        _get_ticks - Retourner le nombre de ticks executée depuis que la scène est active
        """

        return self.runtime_timer

    def update(self) -> None:
        """
        update - Fonction executée à chaque frame pour la logique de la scène
        """

        pass

    def draw(self) -> None:
        """
        draw - Fonction executée à chaque frame pour le rendu de la scène
        """

        pass


class SceneManager(context.Context):
    """
    SceneManager - Orchestrer l'affichage et l'exécution des objets Scene
    """

    def __init__(self) -> None:
        super().__init__()

        self.logger = logging.Logger("core.scene_manager")
        self.scene_cache = {}  # Cache optionnel pour recharger plus vite
        self.stack = [Scene()]
        self.active = self.stack[-1]
    
    def _load_scene(self, scene_name: str, use_cache: bool) -> Scene:
        if use_cache and scene_name in self.scene_cache:
            self.logger.log(f"Loaded '{scene_name}' from cache")
            return self.scene_cache[scene_name]

        module_name = f"scenes.{scene_name}"
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            self.logger.error(f"Failed to import scene '{scene_name}': {e}")
            raise

        class_name = _scene_class_name(scene_name)
        try:
            scene_class = getattr(module, class_name)
        except AttributeError:
            raise AttributeError(
                f"The scene '{scene_name}' does not contain a '{class_name}' class."
            )

        scene = scene_class()
        self.scene_cache[scene_name] = scene
        self.logger.success(f"Loaded new scene '{scene_name}'")
        return scene

    def _activate(self, scene_name: str) -> Scene:
        scene = self.stack[-1]
        scene._name = scene_name
        self.game.active_scene = scene
        self.active = scene
        scene.run()
        return scene

    def set_active_scene(
        self, scene_name: str, use_cache: bool = True, empty_stack: bool = True
    ) -> Scene:
        """Remplace la scène active (et éventuellement toute la pile)."""
        self.logger.log(f"Replacing active scene to '{scene_name}'")

        self.game.audio_engine.stop_all()
        self.stack[-1].inactive()

        module_name = self.stack[-1].__module__
        if module_name in sys.modules:
            del sys.modules[module_name]

        if empty_stack:
            self.stack = []

        self.stack.append(self._load_scene(scene_name, use_cache))

        if empty_stack:
            self.game.event_manager.reset()

        return self._activate(scene_name)

    def add_scene(self, scene_name: str, use_cache: bool = True) -> Scene:
        """Empile une nouvelle scène par-dessus la scène active."""
        self.logger.log(f"Adding scene '{scene_name}' on top of the stack")

        self.stack[-1].inactive()
        self.stack.append(self._load_scene(scene_name, use_cache))

        return self._activate(scene_name)


    def update(self) -> None:
        """
        update - Mettre à jour la scène actuelle et incrémenter le timer d'execution
        """

        for action in self.active.actions.get(self.active.runtime_timer, []):
            action()
        
        for function in self.active.update_elements:
            function()

        self.active.update()

        for scene in self.stack[:-1]:
            scene.update()

        self.active.runtime_timer += 1

    def draw(self) -> None:
        """
        draw - Effectuer les opérations de rendu de la scène
        """

        self.active.draw()
        for scene in self.stack[:-1]:
            scene.draw()
