"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg, feste Seeds, zusammen unter 10 Sekunden.

  Dekodierer MaxRects BSSF   gegen  eine Umsetzung, die in jedem Schritt ALLE maximalen leeren Rechtecke nach Definition aus einem Belegungsraster aufzählt (kleine Behälter, Kante 10 bis 14).
  Freie Rechtecke            gegen  das Belegungsraster: nach jedem Schritt genau die maximalen leeren Rechtecke.
  Bester aller Reihenfolgen   gegen  die naive Dekodierung aller Reihenfolgen (n bis 4) und gegen CP-SAT (nie unter dem Optimum), in tests/test_claims.py für n = 7 und 8.
  Zufall                     gegen  `random.Random(seed).random()` (Handwerte in tests/test_algorithm.py) und gegen die Gleichverteilung der Mischungen (n = 3).
  Eigenschaften:  gemeinsames Skalieren, Zustand ist der Anfang der Packung, jede Packung zulässig und nie unter der Schranke, Suche nie schlechter als der Start.
"""

import itertools
import random

import pytest

import rsu_algorithm as A


def instanzen(anzahl, n_lo, n_hi, cap_lo=10, cap_hi=40, seed0=0):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        n = rng.randint(n_lo, n_hi)
        yield cap, tuple((rng.randint(1, cap), rng.randint(1, cap)) for _ in range(n))


def belegung(gesetzt, cap):
    return [[any(x <= c < x + w and y <= r < y + h for (x, y, w, h) in gesetzt) for c in range(cap)] for r in range(cap)]       # raster[reihe][spalte]


def maximale_leere(gesetzt, cap):
    """Alle maximalen leeren Rechtecke (x, y, w, h) nach Definition: leer und in keiner der vier Richtungen um eine Zelle erweiterbar."""
    raster = belegung(gesetzt, cap)

    def leer(x, y, w, h):
        return all(not raster[r][c] for r in range(y, y + h) for c in range(x, x + w))

    gefunden = []
    for x in range(cap):
        for y in range(cap):
            for w in range(1, cap - x + 1):
                for h in range(1, cap - y + 1):
                    if not leer(x, y, w, h):
                        break
                    links = x > 0 and leer(x - 1, y, 1, h)
                    rechts = x + w < cap and leer(x + w, y, 1, h)
                    unten = y > 0 and leer(x, y - 1, w, 1)
                    oben = y + h < cap and leer(x, y + h, w, 1)
                    if not (links or rechts or unten or oben):
                        gefunden.append((x, y, w, h))
    return gefunden


def maxrects_naiv(rects, order, cap):
    """MaxRects BSSF ohne gepflegte Liste: der freie Platz wird vor jedem Rechteck aus den gesetzten Rechtecken neu aufgezählt."""
    gesetzt = []                                   # je Behälter
    platz = []
    for i in order:
        w, h = rects[i]
        wahl = None
        for b, lst in enumerate(gesetzt):
            for (fx, fy, fw, fh) in maximale_leere(lst, cap):
                if w <= fw and h <= fh:
                    score = (min(fw - w, fh - h), max(fw - w, fh - h), fy, fx)
                    if wahl is None or score < wahl[0]:
                        wahl = (score, b, fx, fy)
            if wahl is not None:
                break
        if wahl is None:
            gesetzt.append([])
            wahl = (None, len(gesetzt) - 1, 0, 0)
        _, b, x, y = wahl
        gesetzt[b].append((x, y, w, h))
        platz.append((i, b, x, y))
    return platz


def test_dekodierer_gegen_die_aufzaehlung_aller_maximalen_leeren_rechtecke():
    for cap, rects in instanzen(16, 1, 9, cap_lo=10, cap_hi=14, seed0=500):
        rng = random.Random(cap)
        for order in (A.reihenfolge_flaeche(rects), rng.sample(range(len(rects)), len(rects))):
            assert A.pack(rects, order, cap)[1] == maxrects_naiv(rects, order, cap), (cap, rects, order)


def test_freie_rechtecke_sind_nach_jedem_schritt_genau_die_maximalen_leeren_rechtecke():
    for cap, rects in instanzen(12, 1, 8, cap_lo=10, cap_hi=14, seed0=700):
        order = A.reihenfolge_flaeche(rects)
        for k in range(len(order) + 1):
            bins, platz, zustand = A.pack(rects, order[:k], cap)
            for b, frei in enumerate(zustand):
                gesetzt = [(x, y, rects[i][0], rects[i][1]) for i, bb, x, y in platz if bb == b]
                assert sorted(frei) == sorted(maximale_leere(gesetzt, cap)), (cap, rects, k, b)


def test_vereinigung_der_freien_rechtecke_ist_die_leere_flaeche():
    for cap, rects in instanzen(12, 1, 8, cap_lo=10, cap_hi=14, seed0=900):
        bins, platz, zustand = A.pack(rects, list(range(len(rects))), cap)
        for b, frei in enumerate(zustand):
            gesetzt = [(x, y, rects[i][0], rects[i][1]) for i, bb, x, y in platz if bb == b]
            raster = belegung(gesetzt, cap)
            for r in range(cap):
                for c in range(cap):
                    in_frei = any(fx <= c < fx + fw and fy <= r < fy + fh for fx, fy, fw, fh in frei)
                    assert in_frei == (not raster[r][c]), (cap, rects, b, r, c)


def test_anfang_der_reihenfolge_ist_der_anfang_der_packung():
    for cap, rects in instanzen(25, 2, 12, cap_lo=10, cap_hi=40, seed0=1100):
        order = A.reihenfolge_flaeche(rects)
        voll = A.pack(rects, order, cap)[1]
        for k in range(len(order) + 1):
            assert A.pack(rects, order[:k], cap)[1] == voll[:k]


def test_alle_packungen_sind_zulaessig_und_nie_unter_der_schranke():
    for cap, rects in instanzen(40, 1, 25, cap_lo=10, cap_hi=100, seed0=1000):
        rng = random.Random(cap)
        for order in (A.reihenfolge_flaeche(rects), rng.sample(range(len(rects)), len(rects))):
            bins, platz, _ = A.pack(rects, order, cap)
            assert A.packung_pruefen(rects, platz, cap) and len(bins) >= A.schranke(rects, cap), (cap, rects)
            for b in bins:
                assert sum(rects[i][0] * rects[i][1] for i in b) <= cap * cap


def test_gemeinsames_skalieren_aendert_die_behaelterzahl_nicht():
    for cap, rects in instanzen(25, 1, 12, cap_lo=10, cap_hi=30, seed0=1300):
        gross = tuple((3 * w, 3 * h) for w, h in rects)
        order = A.reihenfolge_flaeche(rects)
        assert A.reihenfolge_flaeche(gross) == order
        assert len(A.pack(gross, order, 3 * cap)[0]) == len(A.pack(rects, order, cap)[0]), (cap, rects)


def test_bester_aller_reihenfolgen_gegen_naive_dekodierung_und_nie_unter_der_schranke():
    for cap, rects in instanzen(10, 1, 4, cap_lo=8, cap_hi=10, seed0=1500):
        naiv = min(len({b for _, b, _, _ in maxrects_naiv(rects, p, cap)}) for p in itertools.permutations(range(len(rects))))
        assert A.bester_aller_reihenfolgen(rects, cap) == naiv >= A.schranke(rects, cap), (cap, rects)
        assert naiv <= len({b for _, b, _, _ in maxrects_naiv(rects, A.reihenfolge_flaeche(rects), cap)})


def test_bester_aller_reihenfolgen_nie_unter_dem_optimum_von_cpsat():
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    for cap, rects in instanzen(6, 3, 6, cap_lo=10, cap_hi=20, seed0=1700):
        beste = A.bester_aller_reihenfolgen(rects, cap)
        opt = beste if beste == A.schranke(rects, cap) else optimum_cpsat(rects, cap, beste, 20.0, 2)
        assert 0 < A.schranke(rects, cap) <= opt <= beste, (cap, rects)


def test_suche_ist_nie_schlechter_als_der_start_und_liefert_zulaessige_packungen():
    for cap, rects in instanzen(20, 2, 14, cap_lo=20, cap_hi=100, seed0=1900):
        start = A.bewerten(rects, A.reihenfolge_flaeche(rects), cap)
        for methode in (1, 2, 3):
            beste, verlauf = A.suche(rects, cap, methode, 40, 5)
            assert verlauf[-1][0] <= start[0]
            assert A.packung_pruefen(rects, A.pack(rects, beste, cap)[1], cap)


def test_mischungen_sind_gleichverteilt():
    zaehler = {}
    for seed in range(6000):
        p = tuple(A.Zufall(seed).mischen(range(3)))
        zaehler[p] = zaehler.get(p, 0) + 1
    assert set(zaehler) == set(itertools.permutations(range(3)))
    assert all(850 <= c <= 1150 for c in zaehler.values()), zaehler          # Erwartung 1000, Streuung etwa 29
    paare = {}
    for seed in range(6000):
        p = A.Zufall(seed).paar(4)
        paare[p] = paare.get(p, 0) + 1
    assert len(paare) == 12 and all(400 <= c <= 600 for c in paare.values()), paare            # Erwartung 500
