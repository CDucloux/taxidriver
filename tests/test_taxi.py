"""Description.
Tests unitaires du module `libtaxi`.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import matplotlib
import networkx as nx
from source.libtaxi import (
    Emplacement,
    Itineraire,
    Ville,
    _convertit_en_nx,
    carte_graphe,
    _determine_probleme,
    determine_trajet,
    genere_bouchons,
    genere_travaux,
    CARTE_VILLE,
    EmplacementInconnu,
    MemeEmplacement,
    PasDeChemin,
)

matplotlib.use("Agg")  # backend graph


def test_arretes_1():
    with pytest.raises(ValueError):
        Ville(
            emplacements=[Emplacement(1), Emplacement(2)],
            arretes=[(Emplacement(1), Emplacement(2), -1.0)],
        )


def test_arretes_2():
    with pytest.raises(ValueError):
        Ville(
            emplacements=[Emplacement(1), Emplacement(2)],
            arretes=[(Emplacement(1), Emplacement(2), 0.0)],
        )


def test_emplacement_1():
    with pytest.raises(ValueError):
        Ville(
            emplacements=[Emplacement(1), Emplacement(2)],
            arretes=[(Emplacement(3), Emplacement(2), 1.0)],
        )


def test_emplacement_2():
    Ville(
        emplacements=[Emplacement(1), Emplacement(3)],
        arretes=[(Emplacement(1), Emplacement(3), 9.0)],
    )


def test_itineraire_1():
    with pytest.raises(ValueError):
        Itineraire(etapes=[Emplacement(1), Emplacement(1)])


def test_itineraire_2():
    Itineraire(etapes=[Emplacement(1), Emplacement(2)])


def test_conversion_nx():
    e_1, e_2, e_3 = Emplacement(1), Emplacement(2), Emplacement(3)
    ville = Ville(
        emplacements=[e_1, e_2, e_3],
        arretes=[(e_1, e_2, 5.0), (e_1, e_3, 9.0)],
    )
    calcule = _convertit_en_nx(ville)
    attendu = nx.Graph()
    attendu.add_nodes_from([e_1, e_2, e_3])
    attendu.add_edges_from(
        [
            (e_1, e_2, {"duree": 5.0}),
            (e_1, e_3, {"duree": 9.0}),
        ]
    )
    assert nx.utils.graphs_equal(calcule, attendu)


def test_determine_probleme_1():
    depart = Emplacement(18)
    arrivee = Emplacement(1)
    ville = CARTE_VILLE

    with pytest.raises(EmplacementInconnu):
        _determine_probleme(depart=depart, arrivee=arrivee, ville=ville)


def test_determine_probleme_3():
    depart = Emplacement(1)
    arrivee = Emplacement(1)
    ville = CARTE_VILLE

    with pytest.raises(MemeEmplacement):
        _determine_probleme(depart=depart, arrivee=arrivee, ville=ville)


def test_determine_probleme_4():
    depart = Emplacement(1)
    arrivee = Emplacement(4)
    ville = CARTE_VILLE

    assert (_determine_probleme(depart=depart, arrivee=arrivee, ville=ville)) is False


def test_graphe_1():
    ville = CARTE_VILLE
    resultat = carte_graphe(ville)
    assert isinstance(resultat, nx.Graph)


def test_graphe_2():
    ville = CARTE_VILLE
    itineraire = Itineraire(etapes=[Emplacement(2), Emplacement(5), Emplacement(10)])
    resultat = carte_graphe(ville=ville, itineraire=itineraire)
    assert isinstance(resultat, nx.Graph)


def test_graphe_3():
    ville = CARTE_VILLE
    travaux = [Emplacement(1), Emplacement(2), Emplacement(3)]
    resultat = carte_graphe(ville=ville, travaux=travaux)
    assert isinstance(resultat, nx.Graph)


def test_trajet_1():
    e_1, e_2, e_5 = Emplacement(1), Emplacement(2), Emplacement(5)
    ville = Ville(
        emplacements=[e_1, e_2, e_5],
        arretes=[(e_1, e_2, 5.0)],
    )
    with pytest.raises(PasDeChemin):
        determine_trajet(depart=e_1, arrivee=e_5, ville=ville)


def test_trajet_2():
    e_1, e_2, e_3 = Emplacement(1), Emplacement(2), Emplacement(3)
    ville = Ville(
        emplacements=[e_1, e_2, e_3], arretes=[(e_1, e_2, 8.0), (e_2, e_3, 7.0)]
    )
    assert (
        determine_trajet(depart=e_1, arrivee=e_3, ville=ville)
        == Itineraire(
            etapes=[Emplacement(nom=1), Emplacement(nom=2), Emplacement(nom=3)]
        )
    ) is True


##### Tests unitaires sur l'implémentation des bouchons


def test_bouchons_1():
    e_1, e_2, e_8 = Emplacement(1), Emplacement(2), Emplacement(8)
    ville = Ville(
        emplacements=[e_1, e_2, e_8], arretes=[(e_1, e_2, 4.0), (e_1, e_8, 4.0)]
    )

    # gérer les cas différents et surtout avec assert
    genere_bouchons(depart=e_1, arrivee=e_8, ville=ville, duree=8)


##### Tests unitaires sur l'implémentation des travaux à faire
