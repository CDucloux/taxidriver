"""# libtaxi

`libtaxi` est un module Python qui permet de modéliser une ville desservie par un taxi à partir de data structures.

- Il est possible de visualiser la ville (emplacements et routes) ainsi que modifier ses caractéristiques.

/!\ Limites : La carte de la ville "vit" uniquement en mémoire.

L'importation classique du module se fait comme suit ::

    import libtaxi as lt

Développé par :
    - Corentin Ducloux (https://github.com/CDucloux/)
    - Aybuké Bicat (https://github.com/aybuke-b)
"""


from dataclasses import dataclass
import networkx as nx
import copy
import matplotlib.pyplot as plt


@dataclass(frozen=True)
class Emplacement:
    """Représente un emplacement de la ville.

    `nom`: entier correspondant à un numéro d'emplacement

    - On vérifie après l'instanciation que le numéro d'emplacement n'est pas incohérent (< 0)

    Exemple :
    >>> emplacement = Emplacement(nom=1)
    >>> emplacement
    ... Emplacement(nom=1)
    """

    nom: int

    def __post_init__(self):
        if self.nom < 0:
            raise ValueError("L'emplacement doit être un entier positif.")

    def __str__(self):
        return str(self.nom)


@dataclass
class Itineraire:
    """Représente l'itinéraire qu'un client souhaite emprunter.

    `etapes`: liste d'entiers correspondant à des emplacements

    - On vérifie après l'instanciation que l'itinéraire est cohérent, c'est à dire =>
        - Il n'y a pas deux fois le même point
        - Il y au moins deux points dans l'itinéraire

    Exemple :
    >>> sentier = Itineraire(
    ...     etapes=[Emplacement(nom=1), Emplacement(nom=4), Emplacement(nom=9)]
    ... )
    >>> sentier
    ... Itineraire(etapes=[Emplacement(nom=1), Emplacement(nom=4), Emplacement(nom=9)])
    """

    etapes: list[Emplacement]

    def __post_init__(self):
        if len(set(self.etapes)) != len(self.etapes):
            raise ValueError("L'itinéraire comporte deux mêmes points.")
        elif len(self.etapes) == 1:
            raise ValueError("L'itinéraire ne comporte pas assez de points.")


@dataclass
class Ville:
    """Représentation de la carte de la ville.

    `emplacements`: liste d'entiers correspondant à des emplacements présents dans la ville
    `arretes`: liste contenant un tuple de deux emplacements et une durée associée

    - On vérifie après l'instanciation que la carte de la ville est cohérente, c'est à dire =>
        - Les durées de trajet sont strictement positives
        - Un emplacement non-spécifié dans la liste emplacements n'existe pas dans la ville

    Exemple :

    >>> village = Ville(
    ...     emplacements=[Emplacement(nom=2), Emplacement(nom=3), Emplacement(nom=4)],
    ...     arretes=[
    ...         (Emplacement(nom=2), Emplacement(nom=3), 4.0),
    ...         (Emplacement(nom=2), Emplacement(nom=4), 2.0),
    ...         (Emplacement(nom=3), Emplacement(nom=4), 1.0),
    ...     ]
    ... )
    >>> village
    ... Ville(emplacements=[Emplacement(nom=2), Emplacement(nom=3), Emplacement(nom=4)],
    ... arretes=[(Emplacement(nom=2), Emplacement(nom=3), 4.0), (Emplacement(nom=2),
    ... Emplacement(nom=4), 2.0), (Emplacement(nom=3), Emplacement(nom=4), 1.0)])
    """

    emplacements: list[Emplacement]
    arretes: list[tuple[Emplacement, Emplacement, float]]

    def __post_init__(self):
        if any(poids <= 0 for _, _, poids in self.arretes):
            raise ValueError("Les durées des trajets sont forcément positives!")

        for depart, arrivee, _ in self.arretes:
            if depart not in self.emplacements:
                raise ValueError(f"L'emplacement {depart} n'existe pas dans la ville !")
            if arrivee not in self.emplacements:
                raise ValueError(
                    f"L'emplacement {arrivee} n'existe pas dans la ville !"
                )

    def __deepcopy__(self):
        cls = self.__class__
        nouvelle_ville = cls.__new__(cls)
        nouvelle_ville.emplacements = copy.deepcopy(self.emplacements)
        nouvelle_ville.arretes = copy.deepcopy(self.arretes)
        return nouvelle_ville


def _convertit_en_nx(ville: Ville) -> nx.Graph:
    """Crée un graphe networkx à partir de la carte de la ville.

    Exemple :

    >>> village = Ville(
    ...     emplacements=[Emplacement(nom=2), Emplacement(nom=3), Emplacement(nom=4)],
    ...     arretes=[
    ...         (Emplacement(nom=2), Emplacement(nom=3), 4.0),
    ...         (Emplacement(nom=2), Emplacement(nom=4), 2.0),
    ...         (Emplacement(nom=3), Emplacement(nom=4), 1.0),
    ...     ]
    ... )
    >>> convertisseur = _convertit_en_nx(village)
    >>> convertisseur
    ... <networkx.classes.graph.Graph at 0x22a823e6290>
    """
    resultat = nx.Graph()
    resultat.add_nodes_from(ville.emplacements)
    resultat.add_edges_from(
        (depart, arrivee, {"duree": poids}) for depart, arrivee, poids in ville.arretes
    )
    return resultat


class PasDeChemin(Exception):
    pass


class EmplacementInconnu(Exception):
    pass


class MemeEmplacement(Exception):
    pass


class DureeNegative(Exception):
    pass


class ArreteInexistante(Exception):
    pass


def _determine_probleme(
    depart: Emplacement, arrivee: Emplacement, ville: Ville
) -> bool:
    """Fonction renvoyant un booléen qui détermine les problèmes potentiels dans des itinéraires.

    Plus précisément :

    - Si le départ spécifié n'est pas dans la liste des emplacements disponibles
    - Si l'arrivée spécifiée n'est pas dans la liste des emplacements disponibles
    - Si le départ et l'arrivée sont les mêmes points, il n'y a pas d'itinéraire

    Si tous les tests passent sans erreur, la fonction renvoie "False".

    Exemple :

    >>> village = Ville(
    ...     emplacements=[Emplacement(nom=2), Emplacement(nom=3), Emplacement(nom=4)],
    ...     arretes=[
    ...         (Emplacement(nom=2), Emplacement(nom=3), 4.0),
    ...         (Emplacement(nom=2), Emplacement(nom=4), 2.0),
    ...         (Emplacement(nom=3), Emplacement(nom=4), 1.0),
    ...     ]
    ... )
    >>> chemin = Itineraire(
    ... etapes=[Emplacement(nom=2), Emplacement(nom=4)]
    ... )
    >>> _determine_probleme(Emplacement(nom=2), Emplacement(nom=3), ville=village)
    ... False
    """

    if all(depart != emplacement for emplacement in ville.emplacements):
        raise EmplacementInconnu(
            f"Attention, {depart} n'est pas un emplacement valide !"
        )
    if all(arrivee != emplacement for emplacement in ville.emplacements):
        raise EmplacementInconnu(
            f"Attention, {arrivee} n'est pas un emplacement valide !"
        )
    if depart == arrivee:
        raise MemeEmplacement(
            "Attention, le point de départ et le point d'arrivée spécifiés sont les mêmes !"
        )
    return False


def carte_graphe(
    ville: Ville, itineraire: Itineraire = None, travaux: list[Emplacement] = None
) -> nx.Graph:
    """Crée la représentation graphique d'une carte avec des points donnés.

    - La carte peut afficher un itinéraire => les emplacements empruntés seront affichés en rouge
    - La carte peut afficher des travaux => Les emplacements affectés seront affichés en jaune
    - Les emplacements non-affectés par des travaux et des itinéraires sont affichés en vert

    Exemples :

    >>> village = Ville(
    ...     emplacements=[Emplacement(nom=2), Emplacement(nom=3), Emplacement(nom=4)],
    ...     arretes=[
    ...         (Emplacement(nom=2), Emplacement(nom=3), 4.0),
    ...         (Emplacement(nom=2), Emplacement(nom=4), 2.0),
    ...         (Emplacement(nom=3), Emplacement(nom=4), 1.0),
    ...     ]
    ... )
    >>> chemin = Itineraire(
    ... etapes=[Emplacement(nom=2), Emplacement(nom=4)]
    ... )
    >>> travaux = [Emplacement(nom=2), Emplacement(nom=3)]
    >>> graph = carte_graphe(ville=village)
    >>> graph_chemin = carte_graphe(ville=village, itineraire=chemin)
    >>> graph_travaux = carte_graphe(ville=village, travaux=travaux)
    """

    resultat = _convertit_en_nx(ville)
    positions = nx.spring_layout(resultat)
    edge_labels = {(a, b): p["duree"] for a, b, p in resultat.edges(data=True)}
    nx.draw_networkx_edges(resultat, positions, edge_color="gray")
    nx.draw_networkx_edge_labels(resultat, positions, edge_labels=edge_labels)
    nx.draw_networkx_labels(resultat, positions)

    if itineraire:

        _determine_probleme(
            depart=itineraire.etapes[0], arrivee=itineraire.etapes[-1], ville=ville
        )
        nodes_visites = itineraire.etapes
        node_colors = [
            "red" if node in nodes_visites else "green" for node in resultat.nodes()
        ]
        nx.draw_networkx_nodes(
            resultat, positions, node_color=node_colors, node_size=500
        )
        plt.title("Carte de la ville avec l'itinéraire emprunté")
    elif travaux:
        node_colors = ["yellow" if e in travaux else "green" for e in resultat.nodes()]
        nx.draw_networkx_nodes(
            resultat,
            positions,
            node_color=node_colors,
            node_size=500,
        )
        plt.title("Carte de la ville avec travaux")
    else:
        nx.draw_networkx_nodes(resultat, positions, node_color="green", node_size=500)
        plt.title("Carte de la ville")

    plt.show()

    return resultat


def determine_trajet(
    depart: Emplacement, arrivee: Emplacement, ville: Ville
) -> Itineraire:
    """Détermine le trajet le plus court possible d'un emplacement à un autre.

    - Vérifie d'abord que le trajet est cohérent avec la fonction _determine_probleme
    - Convertit la ville en graph nx
    - Renvoie l'itinéraire le plus court entre les points spécifiés
    - Renvoie l'exception Pas de Chemin si les emplacements ne sont pas connectés

    Exemple :

    >>> determine_trajet(depart = Emplacement(nom=2), arrivee = Emplacement(nom=3), ville=village)
    ... Itineraire(etapes=[Emplacement(nom=2), Emplacement(nom=4), Emplacement(nom=3)])
    """
    _determine_probleme(depart, arrivee, ville)
    G = _convertit_en_nx(ville)
    try:
        resultat_nx = nx.shortest_path(
            G, source=depart, target=arrivee, weight="duree", method="bellman-ford"
        )
    except nx.exception.NetworkXNoPath:
        raise PasDeChemin(
            f"Les emplacements {depart} et {arrivee} ne sont pas connectés !"
        )
    return Itineraire(etapes=resultat_nx)


def genere_bouchons(
    depart: Emplacement, arrivee: Emplacement, duree: float, ville: Ville
) -> Ville:
    """Génère des bouchons à partir d'une arrête et d'une durée spécifiée.

    - La fonction crée une copie de la ville qu'elle modifie
    - Renvoie la ville associée avec l'arrête dans laquelle le temps de trajet a été modifié

    Exemple :

    >>> genere_bouchons(
    ...     depart=Emplacement(nom=2),
    ...     arrivee=Emplacement(nom=3),
    ...     duree=4.0,
    ...     ville=village
    ... )
    ... Ville(emplacements=[Emplacement(nom=2), Emplacement(nom=3), Emplacement(nom=4)],
    arretes=[(Emplacement(nom=2), Emplacement(nom=3), 8.0), (Emplacement(nom=2), Emplacement(nom=4), 2.0),
    (Emplacement(nom=3), Emplacement(nom=4), 1.0)])
    """
    _determine_probleme(depart, arrivee, ville)
    try:
        i = next(
            i
            for i, (u, v, d) in enumerate(ville.arretes)
            if (u.nom == depart.nom and v.nom == arrivee.nom)
            or (v.nom == depart.nom and u.nom == arrivee.nom)
        )
    except StopIteration as e:
        raise ArreteInexistante(
            f"La route spécifiée entre les emplacements {depart} et {arrivee} n'existe pas !"
        )
    else:
        nouvelle_ville = ville.__deepcopy__()
        u, v, d = nouvelle_ville.arretes[i]

        if (d + duree) <= 0:
            raise DureeNegative(
                "Attention, la durée de la fluidification spécifiée ne respecte pas les durées de trajets !"
            )
        nouvelle_ville.arretes[i] = (u, v, d + duree)
    return nouvelle_ville


def genere_travaux(
    emplacements: list[Emplacement], duree: float, ville: Ville
) -> Ville:
    """Génère des travaux sur un ou plusieurs emplacement(s) spécifié(s) avec une durée variable.

    - La fonction crée une copie de la ville qu'elle modifie
    - Il est possible de changer la durée sur un ou plusieurs emplacements

    Exemple :

    >>> genere_travaux(
    ...    emplacements=[Emplacement(nom=2), Emplacement(nom=3)],
    ...    duree=4.0,
    ...    ville=village
    ... )
    ... Ville(emplacements=[Emplacement(nom=2), Emplacement(nom=3), Emplacement(nom=4)],
    arretes=[(Emplacement(nom=2), Emplacement(nom=3), 12.0), (Emplacement(nom=2), Emplacement(nom=4), 6.0),
    (Emplacement(nom=3), Emplacement(nom=4), 5.0)])
    """
    if len(set(emplacements)) != len(emplacements):
        raise MemeEmplacement(
            "Attention, vous ne pouvez pas sélectionner 2 mêmes emplacements !"
        )
    if duree <= 0:
        raise DureeNegative(
            "Attention, la durée de travaux sur un emplacement doit forcément être positive !"
        )

    nouvelle_ville = ville.__deepcopy__()

    for emplacement in emplacements:
        if emplacement not in nouvelle_ville.emplacements:
            raise EmplacementInconnu(
                f"Attention, {emplacement} n'est pas un emplacement valide !"
            )

    for i, (u, v, d) in enumerate(nouvelle_ville.arretes):
        if u in emplacements and v in emplacements:
            nouvelle_ville.arretes[i] = (u, v, d + duree * 2)
        elif u in emplacements or v in emplacements:
            nouvelle_ville.arretes[i] = (u, v, d + duree)
    return nouvelle_ville


def _constructeur_ville():
    """Construit une ville `constante` à partir de 16 emplacements."""
    (
        e_1,
        e_2,
        e_3,
        e_4,
        e_5,
        e_6,
        e_7,
        e_8,
        e_9,
        e_10,
        e_11,
        e_12,
        e_13,
        e_14,
        e_15,
        e_16,
    ) = emplacements = [
        Emplacement(nom=1),
        Emplacement(nom=2),
        Emplacement(nom=3),
        Emplacement(nom=4),
        Emplacement(nom=5),
        Emplacement(nom=6),
        Emplacement(nom=7),
        Emplacement(nom=8),
        Emplacement(nom=9),
        Emplacement(nom=10),
        Emplacement(nom=11),
        Emplacement(nom=12),
        Emplacement(nom=13),
        Emplacement(nom=14),
        Emplacement(nom=15),
        Emplacement(nom=16),
    ]
    return Ville(
        emplacements=emplacements,
        arretes=[
            (e_1, e_2, 5.0),
            (e_1, e_3, 9.0),
            (e_1, e_4, 4.0),
            (e_2, e_5, 3.0),
            (e_2, e_6, 2.0),
            (e_3, e_4, 4.0),
            (e_3, e_6, 1.0),
            (e_4, e_7, 7.0),
            (e_5, e_8, 4.0),
            (e_5, e_9, 2.0),
            (e_5, e_10, 9.0),
            (e_6, e_7, 3.0),
            (e_6, e_10, 9.0),
            (e_6, e_11, 6.0),
            (e_7, e_11, 8.0),
            (e_7, e_15, 5.0),
            (e_8, e_12, 5.0),
            (e_9, e_8, 3.0),
            (e_9, e_13, 10.0),
            (e_10, e_9, 6.0),
            (e_10, e_13, 5.0),
            (e_10, e_14, 1.0),
            (e_11, e_14, 2.0),
            (e_12, e_16, 9.0),
            (e_13, e_12, 4.0),
            (e_13, e_14, 3.0),
            (e_14, e_16, 4.0),
            (e_15, e_14, 4.0),
            (e_15, e_16, 3.0),
        ],
    )


CARTE_VILLE = _constructeur_ville()
