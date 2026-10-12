"""Tests de la boucle principale de l'agent (run_forever)."""
from unittest.mock import patch

import pytest

from app.agent import run_forever
from app.sender import MetricsDeliveryError


class StopLoop(Exception):
    """Exception de test utilisée pour sortir de la boucle infinie."""


def test_run_forever_stops_on_keyboard_interrupt():
    with patch("app.agent.run_once", side_effect=KeyboardInterrupt), patch(
        "app.agent.time.sleep"
    ) as sleep:
        run_forever()  # doit retourner proprement, sans exception

    sleep.assert_not_called()


def test_run_forever_logs_success_then_continues():
    delivery = {"status_code": 201, "response": {"status": "received"}}

    with patch("app.agent.run_once", return_value=delivery) as run_once, patch(
        "app.agent.time.sleep", side_effect=StopLoop
    ) as sleep:
        with pytest.raises(StopLoop):
            run_forever()

    run_once.assert_called_once()
    sleep.assert_called_once()


def test_run_forever_survives_a_delivery_error():
    with patch(
        "app.agent.run_once", side_effect=MetricsDeliveryError("API indisponible")
    ) as run_once, patch("app.agent.time.sleep", side_effect=StopLoop):
        with pytest.raises(StopLoop):
            run_forever()

    # L'erreur d'envoi est journalisée, la boucle atteint bien le sleep suivant.
    run_once.assert_called_once()
