"""
core.context - Passer simplement l'objet du jeu à n'importe quel élément

EwoFluffy - BrokeTeam - 2026
"""


class GameContext:
    """
    GameContext - Classe pointant vers le contexte du jeu
    """

    _game = None

    @classmethod
    def set_game(cls, game) -> None:
        cls._game = game

    @classmethod
    def get_game(cls):
        return cls._game


class Context:
    """
    Context - Classe destinée à être utilisé pour donner le contexte du moteur et du jeu à une entitée
    """

    def __init__(self) -> None:
        self.game = GameContext.get_game()
        assert type(self.game) is not None