"""
core.error_handler - Gestion des erreurs intégrée avec le module systems.logging

EwoFluffy - BrokeTeam - 2026
"""

import sys

from core.context import GameContext
from systems.logging import Logger


class ErrorHandler(GameContext):
    """
    ErrorHandler - Classe à instance unique destinée à gérer les erreurs d'exécutions
    """

    def __init__(self) -> None:
        self.logger = Logger("components.error_handler")

        sys.excepthook = self._error_handler

        self.logger.success("Registered global error handler")

    def _error_handler(self, exctype, value) -> None:
        """
        _error_handler - Fonction privée remplaçante de l'error-handler par défaut
        """

        if exctype is KeyboardInterrupt:
            self.logger.log("Keyboard Interrupt triggered, exiting...")
            self.logger.success("Have a nice day :3")
        else:
            self.logger.critical("Error occurred D: , now displaying execution dump")
            self.logger.highlight("--------- START OF DUMP ---------")
            for key, value in GameContext.get_game().__dict__.items():
                if key.startswith("__"):
                    continue
                self.logger.log(f"{key}: {type(value).__name__} = {value}")
            self.logger.highlight("--------- END OF DUMP ---------")
            self.logger.critical(
                f"Error of type {exctype.__name__} at context [{value}]"
            )
