"""
main - Entry point of the engine

EwoFluffy - BrokeTeam - 2026
"""

from core.engine import Game
from systems.logging import Logger

logger: Logger = Logger("main")


def main() -> None:
    logger.highlight("Welcome to BrokeOut")
    try:
        Game().run()
    except KeyboardInterrupt:
        pass
    logger.highlight("Have a nive day :D")


if __name__ == "__main__":
    main()
