"""Description.
Tests unitaires du module `libformat`.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import networkx as nx
from source.libtaxi import (
    Emplacement,
    Itineraire,
    Ville,
)
from source.libformat import format_emplacement, format_routes, format_trajet


@pytest.fixture
def simple() -> Ville:
    e_1 = Emplacement(nom=1)
    e_2 = Emplacement(nom=2)
    return Ville(emplacements=[e_1, e_2], arretes=[(e_1, e_2, 2.0)])


@pytest.fixture
def itineraire_simple() -> Itineraire:
    return Itineraire(etapes=[Emplacement(nom=1), Emplacement(nom=2)])


def test_tablo_emplacements(simple):
    calcul = format_emplacement(simple)
    c_1 = calcul.columns[0]
    assert c_1.header == "Emplacements"
    for i, cell in enumerate(c_1.cells):
        assert cell == str(i + 1)


def test_tablo_duree(simple):
    calcul = format_routes(simple)
    c_1, c_2, c_3 = calcul.columns
    assert c_1.header == "Emplacement de départ"
    assert c_2.header == "Emplacement d'arrivée"
    assert c_3.header == "Durée"
    assert next(c_1.cells) == "1"
    assert next(c_2.cells) == "2"
    assert next(c_3.cells) == "2.0 min"


def test_markdown_trajet(itineraire_simple):
    calcul = format_trajet(itineraire_simple)
    assert (
        calcul.parsed[1].content
        == "Itinéraire le plus court pour l'emplacement 1 - 2 :"
    )
    assert (
        calcul.parsed[5].content == "**Le taxi passe par les emplacements suivants** :"
    )
    assert calcul.parsed[11].content == "Emplacement 1 (durée : 5.0 minutes)"
    assert calcul.parsed[16].content == "Emplacement 2"
    assert calcul.parsed[22].content == "`Durée totale du trajet` : 5.0 minutes"
