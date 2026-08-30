"""
systems.logging - module de gestion des logs

EwoFluffy - BrokeTeam - 2026
"""

from datetime import datetime
import colorama

from systems.config import config


class Logger:
    """
    Logger - Gestionnaire de logs du projet
    ---
    Le gestionnaire de logs permet d'afficher dynamiquement des logs dans la console du jeu afin
    de tracer avec précision l'exécution de chaques composants de celui-ci
    """

    def __init__(self, name: str = "Logger element", verbose: bool = True) -> None:
        self.name: str = name

        if verbose:
            self.log(f"Logger element created for {name} as {self}")

    def check_enabled(self, group: str | None) -> bool:
        """
        check_enabled - Vérifier si les logs pour ce composant et ce groupe sont activées
        ---
        params :
            - group : str | None = Nom du groupe à vérifier
        """

        r = False
        if "special.all" in config.debug.logs:
            if config.debug.logs["special.all"]:
                r = True

        if self.name in config.debug.logs:
            if not config.debug.logs[self.name]:
                r = False
            else:
                r = True

        if group is not None:
            if self.name + "." + group in config.debug.logs:
                if not config.debug.logs[self.name + "." + group]:
                    r = False
                else:
                    r = True

        return r

    def log(self, message: str, group: str | None = None) -> None:
        """
        log - Affiche une entrée de type log (niveau 4) dans la console
        """

        if config.engine.log_level > 3 and self.check_enabled(group):
            print(
                f"{colorama.Fore.BLUE}({datetime.now()}) [{self.name}] "
                + f"{message}{colorama.Fore.RESET}"
            )

    def highlight(self, message: str, group: str | None = None) -> None:
        """
        highlight - Affiche une entrée de type highlight (niveau 0) dans la console
        """

        if config.engine.log_level > -1 and self.check_enabled(group):
            print(
                f"{colorama.Back.WHITE}{colorama.Fore.BLACK}({datetime.now()}) [{self.name}] "
                + f"{message}{colorama.Fore.RESET}{colorama.Back.RESET}"
            )

    def warn(self, message: str, group: str | None = None) -> None:
        """
        warn - Affiche une entrée de type warn (niveau 3) dans la console
        """

        if config.engine.log_level > 2 and self.check_enabled(group):
            print(
                f"{colorama.Fore.YELLOW}({datetime.now()})"
                + f"[{self.name}{('.' + group) if group else ''}] "
                + f"{message}{colorama.Fore.RESET}"
            )

    def success(self, message: str, group: str | None = None) -> None:
        """
        success - Affiche une entrée de type success (niveau 4) dans la console
        """

        if config.engine.log_level > 3 and self.check_enabled(group):
            print(
                f"{colorama.Fore.GREEN}({datetime.now()}) "
                + f"[{self.name}{('.' + group) if group else ''}] "
                + f"{message}{colorama.Fore.RESET}"
            )

    def error(self, message: str, group: str | None = None) -> None:
        """
        error - Affiche une entrée de type error (niveau 2) dans la console
        """

        if config.engine.log_level > 1 and self.check_enabled(group):
            print(
                f"{colorama.Fore.RED}({datetime.now()}) [{self.name}{('.' + group) if group else ''}] "
                + f"{message}{colorama.Fore.RESET}"
            )

    def critical(self, message: str, group: str | None = None) -> None:
        """
        critical - Affiche une entrée de type critical (niveau 1) dans la console
        """

        if config.engine.log_level > 0 and self.check_enabled(group):
            print(
                f"{colorama.Back.RED}({datetime.now()}) [{self.name}{('.' + group) if group else ''}] "
                + f"{message}{colorama.Back.RESET}"
            )
