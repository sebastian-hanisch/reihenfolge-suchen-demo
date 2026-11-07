"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rsu_scenario import Instance  # noqa: E402


@pytest.fixture
def mini():
    """Vier Rechtecke (Breite, Höhe) = (5, 4), (9, 2), (3, 5), (3, 2) mit den Nummern 0 bis 3, Behälter 10 mal 10, Fläche 20 + 18 + 15 + 6 = 59, Schranke 1.

    Von Hand gerechnet (Details in tests/test_algorithm.py): Die Reihenfolge nach Fläche (0, 1, 2, 3) braucht 2 Behälter, die Reihenfolge (3, 1, 2, 0) nur 1.
    Das ist auch das Ergebnis des ersten Tauschs der Suche mit der Startzahl 1 (Positionen 0 und 3) und der ersten Zufallsmischung."""
    return Instance(((5, 4), (9, 2), (3, 5), (3, 2)), 10)
