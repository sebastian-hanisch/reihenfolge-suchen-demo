"""Setzt die README zusammen: Tabellen und Text der Annahmen kommen aus denselben Funktionen wie in der App (nur zum Schreiben der README, nicht Teil der Laufzeit).

    python dev/readme_bauen.py [ANZAHL_TESTS]
"""

import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import rsu_algorithm as A  # noqa: E402
import rsu_constants as C  # noqa: E402
import rsu_evaluation as ev  # noqa: E402
from rsu_scenario import beispiel  # noqa: E402

STARTZAHLEN = range(1, 21)          # die 20 Startzahlen der Beispiel-Tabellen


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


@lru_cache(maxsize=None)
def beispiel_zaehlung(quelle: int) -> dict:
    """{(Suche, Budget): Zahl der 20 Startzahlen, bei denen die Suche das Optimum des Beispiels findet}."""
    rects = beispiel(quelle).rects
    opt = C.BEISPIEL_OPTIMUM[quelle]
    return {(m, b): sum(A.suche(rects, C.CAP, m, b, s)[1][-1][0] == opt for s in STARTZAHLEN) for m in ev.SUCHEN_MIT_LAUF for b in C.BUDGETS}


def tabellen():
    """(A, B, C, Beispiel 1, Beispiel 2): A = Behälter über der Vergleichsbasis je Zelle, B = Anteil Optimum getroffen, C = alle Reihenfolgen durchprobiert (n = 7, 8), die Beispiele = Zahl der Startzahlen."""
    spalten = [(m, b) for m in (0, 1, 2, 3) for b in ((C.BUDGETS[-1],) if m == 0 else (C.BUDGETS[1], C.BUDGETS[-1]))]
    kopf = " | ".join(C.SUCHE_KURZ[m] + ("" if m == 0 else f" {b}") for m, b in spalten)
    ta = ["| Verteilung | n | Basis | " + kopf + " |", "|---|---|---|" + "---|" * len(spalten)]
    for v in range(len(C.VERTEILUNGEN)):
        for ni, n in enumerate(C.MESS_N):
            z = ev.zeile(v, ni)
            b, m = ev.referenz(z)
            ta.append(f"| {C.VERTEILUNG_KURZ[v]} | {n} | {'Optimum' if b == 'dem Optimum' else 'Schranke'} | " + " | ".join(de(m[s][bu]) for s, bu in spalten) + " |")
    tb = ["| Verteilung | n | Fläche | Zufall | Tausch B | Tausch B+F |", "|---|---|---|---|---|---|"]
    for r in ev.optimum_zeilen():
        tb.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]} | {r['n']} | {r['flaeche']:.0f} % | {r['zufall']:.0f} % | {r['tausch_b']:.0f} % | {r['tausch_bf']:.0f} % |")
    tc = ["| Rechtecke | entschiedene Instanzen | Fläche trifft das Optimum | beste Reihenfolge trifft das Optimum |", "|---|---|---|---|"]
    for r in ev.obergrenze_zeilen():
        tc.append(f"| {r['n']} | {r['entschieden']} von {r['instanzen']} | {r['flaeche_trifft']} | {r['beste_trifft']} |")
    bsp = []
    for q in (0, 1):
        z = beispiel_zaehlung(q)
        zeilen = ["| Suche | " + " | ".join(f"{b} Auswertungen" for b in C.BUDGETS) + " |", "|---|---|---|---|"]
        for m in ev.SUCHEN_MIT_LAUF:
            zeilen.append(f"| {C.SUCHE_KURZ[m]} | " + " | ".join(f"{z[(m, b)]} von 20" for b in C.BUDGETS) + " |")
        bsp.append("\n".join(zeilen))
    return "\n".join(ta), "\n".join(tb), "\n".join(tc), bsp[0], bsp[1]


if __name__ == "__main__":
    vorlage = (ROOT / "dev" / "readme_vorlage.md").read_text(encoding="utf-8")
    ta, tb, tc, b1, b2 = tabellen()
    anzahl = sys.argv[1] if len(sys.argv) > 1 else "TESTZAHL"
    text = (vorlage.replace("{{TABELLE_A}}", ta).replace("{{TABELLE_B}}", tb).replace("{{TABELLE_C}}", tc).replace("{{BEISPIEL_1}}", b1).replace("{{BEISPIEL_2}}", b2)
            .replace("{{ANNAHMEN}}", C.ASSUMPTIONS_MARKDOWN).replace("{{TESTS}}", anzahl))
    (ROOT / "README.md").write_text(text, encoding="utf-8")
    print("README.md geschrieben")
