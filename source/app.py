"""Description.
Module contenant l'interface utilisateur de la librairie `lib_taxi`.

- les commandes `bouchons` et `travaux` permettent une interaction utilisateur spécifique pour recalculer ou non un trajet.

Développé par :
    - Corentin Ducloux (https://github.com/CDucloux/)
    - Aybuké Bicat (https://github.com/aybuke-b)
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import typer
from rich import print
from rich.table import Table
from rich.markdown import Markdown
from source import libtaxi as lt
from source import libformat as lf


app = typer.Typer()


@app.command()
def emplacements():
    """Affiche les emplacements desservis par le taxi."""
    print(lf.format_emplacement(lt.CARTE_VILLE))


@app.command()
def routes(graphe: bool = False):
    """Affiche les routes reliées de la ville.

    Arguments:
    --graphe : Si vrai, affiche la carte de la ville sous forme de graphe, sinon sous forme de tableau.
    """
    if graphe:
        print(lt.carte_graphe(lt.CARTE_VILLE))
    else:
        print(lf.format_routes(lt.CARTE_VILLE))


@app.command()
def trajet(depart: int, arrivee: int, graphe: bool = False):
    """Calcule le trajet optimal entre les points de la ville.

    Arguments:
    --graphe : Si vrai, affiche le trajet sous forme de graphe, sinon sous forme de sortie markdown.
    """
    resultat = None  # pour éviter les problèmes d'assignement du try except
    try:
        resultat = lt.determine_trajet(
            depart=lt.Emplacement(nom=depart),
            arrivee=lt.Emplacement(nom=arrivee),
            ville=lt.CARTE_VILLE,
        )
    except lt.PasDeChemin as e:
        print(e)
    except lt.EmplacementInconnu as e:
        print(e)
    except lt.MemeEmplacement as e:
        print(e)
        pass
    if graphe:
        print(lt.carte_graphe(lt.CARTE_VILLE, resultat))
    else:
        if resultat is None:
            pass
        else:
            print(lf.format_trajet(resultat))


@app.command()
def bouchons(depart: int, arrivee: int, duree: float, fluidification: bool = False):
    """Fluidifie ou ralentit la durée de parcours d'une arrête spécifiée.

    Arguments:
    --fluidification : Si vrai, le parcours se fluidifie
    """
    if fluidification:
        duree = -duree
    try:
        lt.CARTE_VILLE = lt.genere_bouchons(
            lt.Emplacement(nom=depart),
            lt.Emplacement(nom=arrivee),
            duree=duree,
            ville=lt.CARTE_VILLE,
        )
    except lt.EmplacementInconnu as e:
        print(e)
    except lt.MemeEmplacement as e:
        print(e)
    except lt.ArreteInexistante as e:
        print(e)
    except lt.DureeNegative as e:
        print(e)
    else:
        routes()
        if fluidification:
            print(
                f":vertical_traffic_light: La route {depart}-{arrivee} a une durée inférieure de {-duree} minutes !"
            )
        else:
            print(
                f":warning: La route {depart}-{arrivee} a {duree} minutes de bouchons !"
            )
        nouvel_itineraire = typer.prompt(
            "Voulez-vous recalculer un nouvel itinéraire ? ",
            type=bool,
            prompt_suffix="",
        )
        if nouvel_itineraire:
            dep_trajet_bouchon = typer.prompt("Départ ", type=int)
            arr_trajet_bouchon = typer.prompt("Arrivée ", type=int)
            graphe = typer.prompt("Graphe ", type=bool)
            if graphe:
                trajet(dep_trajet_bouchon, arr_trajet_bouchon, graphe=True)
            else:
                trajet(dep_trajet_bouchon, arr_trajet_bouchon)
        else:
            pass


@app.command()
def travaux(emplacements: list[int], duree: float):
    """Ajoute des travaux à certains emplacements de la ville."""
    liste_emplacements = [lt.Emplacement(nom=e) for e in emplacements]
    try:
        lt.CARTE_VILLE = lt.genere_travaux(
            emplacements=liste_emplacements, duree=duree, ville=lt.CARTE_VILLE
        )
    except lt.EmplacementInconnu as e:
        print(e)
    except lt.MemeEmplacement as e:
        print(e)
    else:
        routes()
        if len(liste_emplacements) == 1:
            print(
                f":construction: L'emplacement {liste_emplacements[0]} est en travaux ! Durée des travaux : {duree} minutes."
            )
        else:
            print(
                f":construction: Les emplacements {[x.nom for x in liste_emplacements]} sont en travaux ! Durée des travaux : {duree} minutes."
            )
        lt.carte_graphe(travaux=liste_emplacements, ville=lt.CARTE_VILLE)
        nouvel_itineraire = typer.prompt(
            "Voulez-vous recalculer un nouvel itinéraire ? ",
            type=bool,
            prompt_suffix="",
        )
        if nouvel_itineraire:
            dep_trajet_travaux = typer.prompt("Départ ", type=int)
            arr_trajet_travaux = typer.prompt("Arrivée ", type=int)
            graphe = typer.prompt("Graphe ", type=bool)
            if graphe:
                trajet(dep_trajet_travaux, arr_trajet_travaux, graphe=True)
            else:
                trajet(dep_trajet_travaux, arr_trajet_travaux)
        else:
            pass


if __name__ == "__main__":
    app()
