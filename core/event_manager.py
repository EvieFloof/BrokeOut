"""
core.event_manager - Gestionnaire d'évènements de BrokeEngine

EwoFluffy - BrokeTeam - 2026
"""

from typing import TYPE_CHECKING

import pygame

from objects.prototype import Entity
from systems.logging import Logger

class EventManager:
    """
    EventManager - Classe du gestionnaire d'évènements, permet d'envoyer arbitrairement des appels aux fonctions
    selon les évènements de PyGame ainsi que la création d'évènements personnalisés et dynamiquement
    """

    def __init__(self) -> None:
        self.listeners = {}
        self.logger = Logger("core.event_manager")

        self.logger.success("Event manager loaded")

    def subscribe(self, listener, event: str) -> None:
        """
        subscribe - Connecter un objet à un évènement
        La fonction listener.event sera appelée lorsque que celle-ci sera envoyé d'un autre module
        """

        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(listener)
        self.logger.log(f"New subscription from {listener} to event {event}", "subscriptions")
        self.logger.log(str(self.listeners), "verbose")

    def unsubscribe(self, listener, event: str) -> None:
        """
        unsubscribe - Déconnecter un objet d'un évènement
        L'objet listener arrêtera de récupérer l'évènement event
        """

        if event not in self.listeners:
            return
        if listener not in self.listeners[event]:
            return

        self.listeners[event].remove(listener)

        self.logger.log(f"subscription from {listener} to removed", "subscriptions")
        self.logger.log(str(self.listeners), "verbose")

    def send_event(self, event: str) -> None:
        """
        send_event - Envoyer un évènement a toutes les classes abonnées à l'évènement event
        """

        if event not in self.listeners:
            return
        for entity in self.listeners[event]:
            getattr(entity, event)()
            self.logger.log(f"Sent event {event} to object {entity}", "events")

    def handle_events(self) -> bool:
        """
        handle_events - Connecteur pour le gestionnaire d'évènements de PyGame
        """

        for event in pygame.event.get():
            event_name = pygame.event.event_name(event.type)
            self.logger.log(event_name, "event_name")
            if event_name in self.listeners.keys():
                for i in self.listeners[event_name]:
                    self.logger.log(f"Sent event {event} to object {i}", "events")
                    getattr(i, event_name)(event)
        return True

    def reset(self) -> None:
        """
        reset - supprimer toutes les entrées d'évènements
        """

        self.logger.log("Unregistered all listeners")

        self.listeners = {}
