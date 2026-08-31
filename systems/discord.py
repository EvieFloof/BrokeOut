"""
systems.discord - module de l'intégration à Discord

EwoFluffy - BrokeTeam - 2026
"""

import discordrpc
from discordrpc.utils import timestamp

from systems.logging import Logger

DISCORD_APPLICATION_ID = 1425483708424650772
START_TIMESTAMP = timestamp


class DiscordRPC:
    """
    DiscordRPC - Classe gérante de l'intégration du status Discord depuis le jeu
    """

    def __init__(self) -> None:
        self.rpc = discordrpc.RPC(app_id=DISCORD_APPLICATION_ID, output=False)
        self.logger = Logger("systems.discord", True)

    def set_rich_presence(self, title: str, text: str) -> None:
        """
        set_rich_presence - Définir la présence riche sur Discord
        ---
        params:
            - title: str = Titre du status
            - text: str = Text du status
        """

        self.rpc.set_activity(state=text, details=title, ts_start=START_TIMESTAMP)
        self.logger.log(f"Changed current Discord rich presence activity to \"{title}: {text}\"")
