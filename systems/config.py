"""
systems.config - code de connection au fichier de configuration

EwoFluffy - BrokeTeam - 2026
"""

from munch import munchify
import yaml

with open("settings.yaml", "r", encoding="utf8") as stream:
    config = munchify(yaml.safe_load(stream))
