"""Jede Zahl der README und der App-Texte, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

* Das vorberechnete Raster (rsu_precomputed.json): die ersten drei Instanzen jeder der 12 Zellen frisch gerechnet und mit der gespeicherten Stichprobe verglichen, die Zelle „mittel, n = 12“ ganz frisch;
  alle Zellen vollständig prüft `python generate_precomputed.py --check` (parallel, zu lang für jeden Testlauf). Die Optima bei 12 und 20 Rechtecken stammen aus Stück 7 (über Stück 8) und werden
  stichprobenweise mit CP-SAT nachgerechnet (das zeigt zugleich, dass die Instanzen dieser Demo dieselben sind wie dort).
* Die Befunde der README werden aus denselben Auswertungsfunktionen wie in der App berechnet und als Text in der README gesucht.
* Der Text des Expanders „Annahmen, Grenzen und bekannte Probleme“ steht wörtlich in der README.
Dezimalzahlen stehen in der README mit Komma, in der App mit Punkt."""

import itertools
from pathlib import Path

import pytest

import rsu_algorithm as A
import rsu_constants as C
import rsu_evaluation as ev
from rsu_scenario import beispiel, mess_seed, zufallsinstanz

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
ZELLEN = list(itertools.product(range(len(C.VERTEILUNGEN)), range(len(C.MESS_N))))
BUD = C.BUDGETS


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def alle():
    return {(v, ni): ev.zeile(v, ni) for v, ni in ZELLEN}


def gerundete():
    return {k: ev.gerundet(ev.referenz(z)[1]) for k, z in alle().items()}


def _opt(v, ni):
    return ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)].get("opt")


def test_raster_hat_alle_zellen_und_die_parameter():
    daten = ev.vorberechnet()
    assert daten["instanzen"] == C.INSTANZEN == 100 and daten["cap"] == C.CAP == 100 and daten["opt_herkunft"] == C.OPT_HERKUNFT
    assert set(daten["zellen"]) == {ev.zelle_schluessel(v, ni) for v, ni in ZELLEN} and len(ZELLEN) == 12
    assert set(daten["stichprobe"]) == set(daten["zellen"])
    for (v, ni), n in ((k, C.MESS_N[k[1]]) for k in ZELLEN):
        z = daten["zellen"][ev.zelle_schluessel(v, ni)]
        assert ("opt" in z) == (n in C.EXAKT_N)
        if "opt" in z:
            assert len(z["opt"]) == 100
        assert set(daten["stichprobe"][ev.zelle_schluessel(v, ni)]) == {str(j) for j in C.STICHPROBE_J}
    assert set(daten["obergrenze"]) == {str(n) for n in C.OBERGRENZE_N}


@pytest.mark.parametrize("v,ni", ZELLEN)
def test_stichprobe_jeder_zelle_stimmt_mit_frischer_rechnung(v, ni):
    schl = ev.zelle_schluessel(v, ni)
    daten = ev.vorberechnet()
    summe = None
    for j in C.STICHPROBE_J:
        gespeichert = daten["stichprobe"][schl][str(j)]
        assert ev.messzelle(v, ni, _opt(v, ni), [j]) == gespeichert, (schl, j)
        summe = gespeichert if summe is None else {k: _addiere(summe[k], gespeichert[k]) for k in gespeichert}
    # die Stichprobe ist Teil der Zelle: jede Summe der Zelle ist mindestens so groß (alle Beiträge sind nicht negativ)
    zelle = daten["zellen"][schl]
    for k in summe:
        assert _nicht_kleiner(zelle[k], summe[k]), (schl, k)


def _addiere(a, b):
    if isinstance(a, dict):
        return {k: _addiere(a[k], b[k]) for k in a}
    return a + b


def _nicht_kleiner(a, b):
    if isinstance(a, dict):
        return all(_nicht_kleiner(a[k], b[k]) for k in a)
    return a >= b


def test_eine_ganze_zelle_stimmt_mit_frischer_rechnung():
    gespeichert = ev.vorberechnet()["zellen"][ev.zelle_schluessel(0, 0)]
    frisch = ev.messzelle(0, 0, gespeichert["opt"])
    frisch["opt"] = gespeichert["opt"]
    assert frisch == gespeichert


@pytest.mark.parametrize("v,ni", ZELLEN)
def test_summen_sind_in_sich_stimmig(v, ni):
    z = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]
    k = C.INSTANZEN
    assert all(z["ueber_schranke"]["0"][str(b)] == z["ueber_schranke"]["0"][str(BUD[0])] >= 0 for b in BUD)              # die feste Reihenfolge ändert sich mit dem Budget nicht
    assert all(z["besser"]["0"][str(b)] == 0 for b in BUD)
    for m in ("1", "2", "3"):
        zahlen = [z["ueber_schranke"][m][str(b)] for b in BUD]
        assert zahlen == sorted(zahlen, reverse=True) and zahlen[-1] >= 0                                              # mehr Auswertungen sind nie schlechter
        assert [z["besser"][m][str(b)] for b in BUD] == sorted(z["besser"][m][str(b)] for b in BUD) and z["besser"][m][str(BUD[-1])] <= k
        assert z["ueber_schranke"][m][str(BUD[0])] <= z["ueber_schranke"]["0"][str(BUD[0])]                             # nie schlechter als der Start
    if "opt" in z:
        offen = z["opt"].count(-1)
        assert z["entschieden"] == k - offen
        assert z["opt_ueber_schranke"] <= z["entschieden"] and z["opt_minus_schranke"] >= 0
        for m in "0123":
            assert all(0 <= z["trifft_opt"][m][str(b)] <= z["entschieden"] for b in BUD)
            assert all(z["ueber_opt"][m][str(b)] >= 0 for b in BUD)


def test_gespeicherte_optima_liegen_zwischen_schranke_und_der_reihenfolge_nach_flaeche():
    """Für jede entschiedene Instanz bei 12 und 20 Rechtecken: Schranke <= Optimum <= Behälter der Reihenfolge nach Fläche (die Packung mit dieser Zahl existiert)."""
    for v, ni in ZELLEN:
        if C.MESS_N[ni] not in C.EXAKT_N:
            continue
        for j, o in enumerate(_opt(v, ni)):
            if o < 0:
                continue
            inst = zufallsinstanz(v, C.MESS_N[ni], mess_seed(v, ni, j))
            assert A.schranke(inst.rects, inst.cap) <= o <= A.bewerten(inst.rects, A.reihenfolge_flaeche(inst.rects), inst.cap)[0], (v, ni, j)


STICHPROBE = {12: {0: (9, 11), 1: (6, 7), 2: (7, 9), 3: (17, 27)},       # je zwei Instanzen, die CP-SAT in Bruchteilen von Sekunden entscheidet (wie in Stück 7 und 8)
              20: {0: (28, 34), 1: (5, 6), 2: (0, 1), 3: (2, 6)}}


@pytest.mark.parametrize("n", (12, 20))
@pytest.mark.parametrize("v", range(len(C.VERTEILUNGEN)))
def test_stichprobe_der_optima_stimmt_mit_cpsat_ueberein(v, n):
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    ni = C.MESS_N.index(n)
    opt = _opt(v, ni)
    for j in STICHPROBE[n][v]:
        inst = zufallsinstanz(v, n, mess_seed(v, ni, j))
        ober = A.bewerten(inst.rects, A.reihenfolge_flaeche(inst.rects), inst.cap)[0]
        untergrenze = A.schranke(inst.rects, inst.cap)
        ist = ober if ober == untergrenze else optimum_cpsat(inst.rects, inst.cap, ober, 60.0)
        assert ist == opt[j] >= untergrenze, (v, n, j)


def test_beispiele_sind_instanzen_des_rasters_mit_dem_optimum_von_cpsat():
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    for b, j in ((0, 0), (1, 2)):
        inst = zufallsinstanz(0, 12, mess_seed(0, 0, j))
        assert inst.rects == beispiel(b).rects
        ober = A.bewerten(inst.rects, A.reihenfolge_flaeche(inst.rects), inst.cap)[0]
        assert A.schranke(inst.rects, inst.cap) == 2 and ober == 3
        assert optimum_cpsat(inst.rects, inst.cap, ober, 60.0) == _opt(0, 0)[j] == C.BEISPIEL_OPTIMUM[b] == 2


def test_obergrenze_zaehlung_gegen_eine_unabhaengige_rechnung(monkeypatch):
    """Drei Instanzen der Verteilung „klein“ bei n = 7: die Zählung der Obergrenze gegen eine einzeln ausgeschriebene Rechnung mit CP-SAT."""
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    monkeypatch.setitem(C.OBERGRENZE_INSTANZEN, 7, 3)
    z = ev.obergrenze_zelle(2, 7, lambda rects, cap, ober: optimum_cpsat(rects, cap, ober, 30.0, 2))
    flaeche_trifft = beste_trifft = abstand_flaeche = 0
    for j in range(3):
        rects = zufallsinstanz(2, 7, ev.obergrenze_seed(2, 7, j)).rects
        flaeche = len(A.pack(rects, A.reihenfolge_flaeche(rects), C.CAP)[0])
        beste = min(len(A.pack(rects, p, C.CAP)[0]) for p in itertools.permutations(range(7)))
        opt = optimum_cpsat(rects, C.CAP, min(flaeche, beste), 30.0, 2)
        flaeche_trifft += flaeche == opt
        beste_trifft += beste == opt
        abstand_flaeche += flaeche - opt
    assert (z["instanzen"], z["entschieden"], z["flaeche_trifft"], z["beste_trifft"], z["abstand_flaeche"]) == (3, 3, flaeche_trifft, beste_trifft, abstand_flaeche)


def test_gespeicherte_obergrenze_ist_in_sich_stimmig():
    daten = ev.vorberechnet()["obergrenze"]
    for n in C.OBERGRENZE_N:
        for name, *_ in C.VERTEILUNGEN:
            z = daten[str(n)][name]
            assert z["instanzen"] == C.OBERGRENZE_INSTANZEN[n] and z["entschieden"] <= z["instanzen"]
            # beste <= Fläche und beste >= Optimum: trifft die Fläche das Optimum, trifft es auch die beste; jede Instanz, die nur die beste trifft, ist ein Fall „beste besser als Fläche“
            assert z["flaeche_trifft"] <= z["beste_trifft"] <= z["entschieden"]
            assert z["beste_besser_als_flaeche"] >= z["beste_trifft"] - z["flaeche_trifft"]
            assert z["abstand_beste"] >= 0 and z["abstand_flaeche"] >= z["abstand_beste"]


# --- Tabellen der README -------------------------------------------------------------------------------------------------------------------


def test_readme_tabellen_geben_jede_zeile_wieder():
    from dev.readme_bauen import tabellen

    for tabelle in tabellen():
        for zeile in tabelle.split("\n"):
            assert zeile in README, zeile


# --- Befunde der README --------------------------------------------------------------------------------------------------------------------


def test_beispiel_tabellen_der_startzahlen():
    from dev.readme_bauen import beispiel_zaehlung

    eins, zwei = beispiel_zaehlung(0), beispiel_zaehlung(1)
    assert [[eins[(m, b)] for b in BUD] for m in (1, 2, 3)] == [[1, 1, 6], [1, 4, 14], [1, 11, 17]]
    assert [[zwei[(m, b)] for b in BUD] for m in (1, 2, 3)] == [[0, 0, 0], [0, 0, 0], [0, 1, 1]]
    assert "Beispiel 1 (zwölf Rechtecke, Schranke 2, Optimum 2)" in README and "Beispiel 2 (zwölf andere Rechtecke, Schranke 2, Optimum 2)" in README
    assert "Über die Startzahlen 1 bis 20 findet nach 1000 Auswertungen Zufall 6, Tausch B 14 und Tausch B+F 17 von 20 die zwei Behälter" in README
    assert "Von 20 Startzahlen findet höchstens eine die zwei Behälter, und nur die Tausch-Suche mit Zweitziel" in README
    assert README.count("Die Reihenfolge nach Fläche braucht **3** Behälter.") == 2


def test_suche_hilft_bei_mittleren_rechtecken():
    g = gerundete()
    flaeche = {n: g[(0, ni)][0][BUD[-1]] for ni, n in enumerate(C.MESS_N)}
    suche = {n: g[(0, ni)][3][BUD[-1]] for ni, n in enumerate(C.MESS_N)}
    assert (flaeche, suche) == ({12: 0.28, 20: 0.40, 40: 1.12}, {12: 0.02, 20: 0.10, 40: 0.73})
    assert ev.referenz(ev.zeile(0, 0))[0] == ev.referenz(ev.zeile(0, 1))[0] == "dem Optimum" and ev.referenz(ev.zeile(0, 2))[0] == "der Schranke"
    assert ("sinkt der mittlere Abstand zum Optimum nach 1000 Auswertungen mit Tausch B+F bei n = 12 von **0,28** (Fläche) auf **0,02** bis **0,03** und bei n = 20 von **0,40** auf **0,05** bis **0,10** (je nach Startzahl; die Tabelle zeigt die Startzahlen der Demo); "
            "bei n = 40 sinkt der Abstand zur Schranke von **1,12** auf **0,73**") in README


def test_zweitziel_und_zufall_gegen_tausch():
    g = gerundete()
    z, tb, tbf = ({k: x[m][BUD[-1]] for k, x in g.items()} for m in (1, 2, 3))
    assert (sum(tbf[k] < tb[k] for k in g), sum(tbf[k] == tb[k] for k in g), sum(tbf[k] > tb[k] for k in g)) == (8, 4, 0)
    assert (sum(tb[k] < z[k] for k in g), sum(tb[k] == z[k] for k in g), sum(tb[k] > z[k] for k in g)) == (4, 6, 2)
    assert [k for k in g if tb[k] > z[k]] == [(0, 0), (3, 1)] and (tb[(0, 0)], z[(0, 0)], tb[(3, 1)], z[(3, 1)]) == (0.09, 0.05, 0.03, 0.02)
    assert "In allen **12** Zellen liegt Tausch B+F nach 1000 Auswertungen höchstens so weit über der Bezugsgröße wie Tausch B, in **8** Zellen darunter (in 4 gleich; bei anderen Startzahlen liegt B+F ebenfalls in 0 Zellen darüber, die Zahl der Zellen darunter schwankt zwischen 8 und 9)" in README
    assert "nach 1000 Auswertungen in **4** Zellen besser als Zufall, in 6 gleich und in **2** schlechter (mittlere Rechtecke n = 12: 0,09 gegen 0,05; hoch schmal n = 20: 0,03 gegen 0,02)" in README


def test_instanz_fuer_instanz_zaehlungen():
    z = alle()
    besser = [sum(x["besser"][m][BUD[-1]] for x in z.values()) for m in (1, 2, 3)]
    assert besser == [114, 127, 203] and sum(C.INSTANZEN for _ in z) == 1200
    assert "Zufallsstarts bei **114**, Tausch B bei **127**, Tausch B+F bei **203**" in README


def test_optimum_getroffen_und_offene_instanzen():
    zeilen = ev.optimum_zeilen()
    assert len(zeilen) == 8

    def spanne(n, k):
        return (min(round(r[k]) for r in zeilen if r["n"] == n), max(round(r[k]) for r in zeilen if r["n"] == n))

    assert (spanne(12, "flaeche"), spanne(20, "flaeche"), spanne(12, "tausch_bf"), spanne(20, "tausch_bf")) == ((72, 95), (60, 99), (97, 100), (90, 99))
    assert ("trifft das Optimum bei 12 Rechtecken in 72 bis 95 %, bei 20 in 60 bis 99 % der entschiedenen Instanzen; Tausch B+F nach 1000 Auswertungen bei 12 in **97 bis 100 %**, "
            "bei 20 in **90 bis 99 %**") in README
    offen12 = [ev.zeile(v, 0)["offen"] for v in range(4)]
    offen20 = [ev.zeile(v, 1)["offen"] for v in range(4)]
    assert offen12 == [0, 0, 1, 2] and offen20 == [27, 1, 0, 11] and sum(offen12) == 3 and sum(offen20) == 39
    assert "**3** von 400 bei 12 und **39** von 400 bei 20 Rechtecken (**27** bei mittleren, 1 bei breit gestreuten, 0 bei kleinen und 11 bei hohen schmalen)" in README
    assert ev.zeile(0, 1)["entschieden"] == 73 and "bei mittleren Rechtecken sind 27 von 100 offen" in README


def test_obergrenze_in_der_readme():
    zeilen = ev.obergrenze_zeilen()
    assert [(z["n"], z["instanzen"], z["entschieden"], z["flaeche_trifft"], z["beste_trifft"]) for z in zeilen] == [(7, 240, 240, 229, 240), (8, 100, 100, 94, 100)]
    assert sum(z["beste_trifft"] for z in zeilen) == 340 and sum(z["flaeche_trifft"] for z in zeilen) == 323
    assert "liefert die beste aller Reihenfolgen in **340 von 340** Instanzen das Optimum, die Reihenfolge nach Fläche in **323**" in README
    assert "(240 Instanzen mit 7, 100 mit 8 Rechtecken, eigene Seeds, Optimum mit CP-SAT)" in README and C.OBERGRENZE_INSTANZEN == {7: 60, 8: 25}
    assert ev.verdict_obergrenze(zeilen)[0] == "success"


# --- Beispiele und Texte --------------------------------------------------------------------------------------------------------------------


def test_annahmen_text_der_app_steht_woertlich_in_der_readme():
    assert C.ASSUMPTIONS_MARKDOWN in README


def test_zahlen_im_annahmen_text_sind_die_der_konstanten():
    t = C.ASSUMPTIONS_MARKDOWN
    assert f"Behälter {C.CAP} mal {C.CAP}" in t and f"{C.INSTANZEN} Instanzen" in t and "(12, 20, 40)" in t and "bei 12 und 20 Rechtecken" in t and "bei 40 Rechtecken fehlt es" in t
    assert C.MESS_N == (12, 20, 40) and C.EXAKT_N == (12, 20)


def test_readme_nennt_die_verteilungen_und_das_raster_wie_der_code():
    assert "*mittel* (Breite und Höhe 20 bis 60), *breit* (5 bis 70), *klein* (10 bis 40), *hoch schmal* (Breite 5 bis 30, Höhe 30 bis 80)" in README
    assert [(vt[2], vt[3]) for vt in C.VERTEILUNGEN] == [((20, 60), (20, 60)), ((5, 70), (5, 70)), ((10, 40), (10, 40)), ((5, 30), (30, 80))]
    assert "vier Verteilungen × drei Rechteckzahlen (12, 20, 40) × **100 feste Instanzen**" in README
    assert C.BUDGETS == (50, 200, 1000) and "nach 50, 200 und 1000 Auswertungen" in README
    assert "alle 5040 beziehungsweise 40320 Reihenfolgen" in README and (7 * 6 * 5 * 4 * 3 * 2, 8 * 7 * 6 * 5 * 4 * 3 * 2) == (5040, 40320)


def test_readme_hat_keine_offenen_platzhalter_ausser_dem_live_link():
    ohne_link = README.replace("<!-- TODO nach dem Deploy", "")
    assert "{{" not in README and "TESTZAHL" not in README and ohne_link.count("TODO") == 0
