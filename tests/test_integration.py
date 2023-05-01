"""Description.
Tests d'intégration de l'application.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from subprocess import run
from typer.testing import CliRunner
from source.app import app


def test_commande_emplacements():
    resultat = run(["python", "source\\app.py", "emplacements"], capture_output=True)
    decodeur = resultat.stdout.decode("latin").replace(" ", "").replace("\r", "")
    assert decodeur == (
        "Listedes\n"
        "emplacements\n"
        "disponibles\n"
        "+--------------+\n"
        "|Emplacements|\n"
        "|--------------|\n"
        "|1|\n"
        "|2|\n"
        "|3|\n"
        "|4|\n"
        "|5|\n"
        "|6|\n"
        "|7|\n"
        "|8|\n"
        "|9|\n"
        "|10|\n"
        "|11|\n"
        "|12|\n"
        "|13|\n"
        "|14|\n"
        "|15|\n"
        "|16|\n"
        "+--------------+\n"
    )


def test_commande_routes():
    resultat = run(["python", "source\\app.py", "routes"], capture_output=True)
    assert resultat.stdout.decode("latin") == (
        "                     Carte de la ville                      \r\n"
        "+----------------------------------------------------------+\r\n"
        "| Emplacement de départ | Emplacement d'arrivée | Durée    |\r\n"
        "|-----------------------+-----------------------+----------|\r\n"
        "| 1                     | 2                     | 5.0 min  |\r\n"
        "| 1                     | 3                     | 9.0 min  |\r\n"
        "| 1                     | 4                     | 4.0 min  |\r\n"
        "| 2                     | 5                     | 3.0 min  |\r\n"
        "| 2                     | 6                     | 2.0 min  |\r\n"
        "| 3                     | 4                     | 4.0 min  |\r\n"
        "| 3                     | 6                     | 1.0 min  |\r\n"
        "| 4                     | 7                     | 7.0 min  |\r\n"
        "| 5                     | 8                     | 4.0 min  |\r\n"
        "| 5                     | 9                     | 2.0 min  |\r\n"
        "| 5                     | 10                    | 9.0 min  |\r\n"
        "| 6                     | 7                     | 3.0 min  |\r\n"
        "| 6                     | 10                    | 9.0 min  |\r\n"
        "| 6                     | 11                    | 6.0 min  |\r\n"
        "| 7                     | 11                    | 8.0 min  |\r\n"
        "| 7                     | 15                    | 5.0 min  |\r\n"
        "| 8                     | 12                    | 5.0 min  |\r\n"
        "| 9                     | 8                     | 3.0 min  |\r\n"
        "| 9                     | 13                    | 10.0 min |\r\n"
        "| 10                    | 9                     | 6.0 min  |\r\n"
        "| 10                    | 13                    | 5.0 min  |\r\n"
        "| 10                    | 14                    | 1.0 min  |\r\n"
        "| 11                    | 14                    | 2.0 min  |\r\n"
        "| 12                    | 16                    | 9.0 min  |\r\n"
        "| 13                    | 12                    | 4.0 min  |\r\n"
        "| 13                    | 14                    | 3.0 min  |\r\n"
        "| 14                    | 16                    | 4.0 min  |\r\n"
        "| 15                    | 14                    | 4.0 min  |\r\n"
        "| 15                    | 16                    | 3.0 min  |\r\n"
        "+----------------------------------------------------------+\r\n"
    )


def test_commande_routes_graph():
    resultat = run(
        ["python", "source\\app.py", "routes", "--graphe"], capture_output=True
    )
    assert resultat.stdout.decode("latin") == ("Graph with 16 nodes and 29 edges\r\n")


def test_commande_trajet_graph():
    resultat = run(
        ["python", "source\\app.py", "trajet", "9", "15", "--graphe"],
        capture_output=True,
    )
    assert resultat.stdout.decode("latin") == ("Graph with 16 nodes and 29 edges\r\n")


def test_trajet_1():
    runner = CliRunner()

    result = runner.invoke(app, ["trajet", "2", "8"])
    assert result.exit_code == 0
    assert "Le taxi passe par les emplacements suivants" in result.output
    assert "Emplacement 2 (durée : 3.0 minutes)" in result.output
    assert "Emplacement 5 (durée : 4.0 minutes)" in result.output
    assert "Emplacement 8" in result.output
    assert "Durée totale du trajet : 7.0 minutes" in result.output


def test_trajet_2():
    runner = CliRunner()

    result = runner.invoke(app, ["trajet", "2", "18"])
    assert result.exit_code == 0
    assert "Attention, 18 n'est pas un emplacement valide !\n" in result.output

    result = runner.invoke(app, ["trajet", "2", "2"])
    assert result.exit_code == 0
    assert (
        "Attention, le point de départ et le point d'arrivée spécifiés sont les mêmes !"
        in result.output
    )


def test_bouchons_1():
    runner = CliRunner()
    result = runner.invoke(
        app, ["bouchons", "1", "3", "10.0", "--no-fluidification"], input="false\n"
    )
    assert result.exit_code == 0

    result = runner.invoke(
        app,
        ["bouchons", "1", "3", "10.0", "--no-fluidification"],
        input="true\n1\n7\ntrue\n",
    )
    assert result.exit_code == 0

    result = runner.invoke(
        app,
        ["bouchons", "1", "3", "10.0", "--no-fluidification"],
        input="true\n1\n7\nfalse\n",
    )
    assert result.exit_code == 0


def test_bouchons_2():
    runner = CliRunner()
    result = runner.invoke(
        app, ["bouchons", "1", "3", "5.0", "--fluidification"], input="false\n"
    )
    assert result.exit_code == 0

    result = runner.invoke(
        app,
        ["bouchons", "1", "3", "5.0", "--fluidification"],
        input="true\n1\n7\nfalse\n",
    )
    assert result.exit_code == 0

    result = runner.invoke(
        app,
        ["bouchons", "1", "3", "5.0", "--fluidification"],
        input="true\n1\n7\ntrue\n",
    )
    assert result.exit_code == 0


def test_bouchons_3():
    runner = CliRunner()
    result = runner.invoke(
        app, ["bouchons", "1", "18", "5.0", "--no-fluidification"], input="false\n"
    )
    assert "Attention, 18 n'est pas un emplacement valide !" in result.output

    result = runner.invoke(
        app, ["bouchons", "1", "1", "5.0", "--no-fluidification"], input="false\n"
    )
    assert (
        "Attention, le point de départ et le point d'arrivée spécifiés sont les mêmes !"
        in result.output
    )

    result = runner.invoke(
        app, ["bouchons", "1", "6", "5.0", "--no-fluidification"], input="false\n"
    )
    assert (
        "La route spécifiée entre les emplacements 1 et 6 n'existe pas !"
        in result.output
    )


def test_travaux_1():
    runner = CliRunner()
    result = runner.invoke(app, ["travaux", "2", "3", "4", "15.0"], input="false\n")
    assert result.exit_code == 0

    result = runner.invoke(
        app, ["travaux", "2", "3", "4", "15.0"], input="true\n2\n12\nfalse\n"
    )
    assert result.exit_code == 0

    result = runner.invoke(
        app, ["travaux", "2", "3", "4", "15.0"], input="true\n2\n12\ntrue\n"
    )
    assert result.exit_code == 0


def test_travaux_2():
    runner = CliRunner()

    result = runner.invoke(app, ["travaux", "2", "3", "18", "15.0"])
    assert result.exit_code == 0
    assert "Attention, 18 n'est pas un emplacement valide !" in result.output

    result = runner.invoke(app, ["travaux", "2", "2", "3", "15.0"])
    assert result.exit_code == 0
    assert (
        "Attention, vous ne pouvez pas sélectionner 2 mêmes emplacements !"
        in result.output
    )
