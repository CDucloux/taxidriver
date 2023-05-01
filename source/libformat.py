"""# libformat

`libformat` est un module Python à utiliser en conjonction avec le module `libtaxi`.

- Il permet de formater les sorties de `libtaxi` vers des objets rich.

L'importation classique du module se fait comme suit ::

    import libformat as lf

Développé par :
    - Corentin Ducloux (https://github.com/CDucloux/)
    - Aybuké Bicat (https://github.com/aybuke-b)
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rich.table import Table
from rich.markdown import Markdown
from source import libtaxi as lt

def format_trajet(itineraire: lt.Itineraire) -> Markdown:
    """Transforme un `itineraire` brut en rendu `Markdown`."""
    duree_totale = 0
    texte = f"""
# Itinéraire le plus court pour l'emplacement {itineraire.etapes[0]} - {itineraire.etapes[-1]} :\n"""
    texte += "> **Le taxi passe par les emplacements suivants** : \n"
    for i, etape in enumerate(itineraire.etapes):
        texte += f"- Emplacement {etape.nom}"
        if i < len(itineraire.etapes) - 1:
            for arrete in lt.CARTE_VILLE.arretes:
                if (
                    arrete[0].nom == etape.nom
                    and arrete[1].nom == itineraire.etapes[i + 1].nom
                ) or (
                    arrete[0].nom == itineraire.etapes[i + 1].nom
                    and arrete[1].nom == etape.nom
                ):
                    duree_totale += arrete[2]
                    texte += f" (durée : {arrete[2]} minutes)"
                    break
        texte += "\n"
    texte += "*** \n"
    texte += f"`Durée totale du trajet` : {duree_totale} minutes"
    return Markdown(texte)


def format_routes(ville: lt.Ville) -> Table:
    """Transforme les routes disponibles entre les emplacements en tableau `Markdown`."""
    tablo = Table(title="Carte de la ville")
    tablo.add_column("Emplacement de départ", style="magenta")
    tablo.add_column("Emplacement d'arrivée", style="cyan")
    tablo.add_column("Durée")
    for g1, g2, duree in ville.arretes:
        tablo.add_row(str(g1.nom), str(g2.nom), str(duree) + " min")
    return tablo


def format_emplacement(ville: lt.Ville) -> Table:
    """Transforme les emplacements disponibles en tableau `Markdown`"""
    tablo = Table(title="Liste des emplacements disponibles")
    tablo.add_column("Emplacements")
    for emplacement in ville.emplacements:
        tablo.add_row(str(emplacement.nom))
    return tablo
